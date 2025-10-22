"""Core financial processing logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .config import AppConfig
from .constants import (
    ADMIN_EXPENSES_PATTERN,
    OTHER_EXPENSES_PATTERN,
    SALES_COSTS_PATTERN,
    PRODUCTION_COSTS_PATTERN,
    DEPRECIATION_PATTERNS,
    INTEREST_PATTERNS,
    SALARY_PATTERNS,
    SEVERANCE_PATTERNS,
    ASSET_CLASS_CODE,
    LIABILITY_CLASS_CODE,
    EQUITY_CLASS_CODE,
    CURRENT_ASSET_GROUPS,
    INVENTORY_GROUP_CODE,
    INCOME_DESCRIPTION,
    COST_DESCRIPTION,
    PROFIT_DESCRIPTION,
)
from .data_loader import FinancialData


@dataclass
class BudgetResult:
    summary: pd.DataFrame
    distribution: pd.DataFrame
    gastos_admin: float
    gastos_otros: float
    costos_venta: float
    costos_produccion: float


@dataclass
class KPIResult:
    table: pd.DataFrame
    metrics: Mapping[str, float]


def consolidate_balance(data: FinancialData, config: AppConfig) -> pd.DataFrame:
    sheets = []
    for month in config.month_order:
        sheet_name = f"BALANCE {month}"
        if sheet_name not in data.workbook.sheet_names:
            continue
        df_month = pd.read_excel(data.workbook, sheet_name=sheet_name, skiprows=4)
        if df_month.empty:
            continue
        df_month.columns = (
            [
                "Nivel",
                "Código cuenta contable",
                "Nombre cuenta contable",
                "Saldo inicial",
                "Movimiento débito",
                "Movimiento crédito",
                "Saldo final",
            ]
            + [f"Extra_{i}" for i in range(len(df_month.columns) - 7)]
        )[: len(df_month.columns)]
        df_month["Month"] = month
        sheets.append(df_month)

    if not sheets:
        raise ValueError("No balance sheets were processed")

    consolidated = pd.concat(sheets, ignore_index=True)
    return consolidated[consolidated["Nivel"] == "Clase"].copy()


def _calculate_income(data: FinancialData) -> float:
    """Calculate actual income from income statement.
    
    Args:
        data: Financial data containing income statement
        
    Returns:
        Actual income amount
    """
    ingresos_series = data.resultado[
        data.resultado["Descripcion"].str.contains(INCOME_DESCRIPTION, case=False, na=False)
    ][data.resultado_current_col]
    return abs(float(ingresos_series.iloc[0])) if not ingresos_series.empty else 0.0


def _categorize_expenses(data: FinancialData) -> tuple[dict[str, float], dict[str, float]]:
    """Categorize expenses into different types.
    
    Args:
        data: Financial data containing ERI information
        
    Returns:
        Tuple of (base_expenses, extra_expenses) dictionaries
    """
    # Enhanced expense categorization with better mapping
    base_masks = {
        "gastos_admin": data.eri["Codigo"].str.match(ADMIN_EXPENSES_PATTERN, na=False),
        "gastos_otros": data.eri["Codigo"].str.match(OTHER_EXPENSES_PATTERN, na=False),
        "costos_venta": data.eri["Codigo"].str.match(SALES_COSTS_PATTERN, na=False),
        "costos_prod": data.eri["Codigo"].str.match(PRODUCTION_COSTS_PATTERN, na=False),
    }

    # Additional categorization for salaries and severance
    salary_pattern = "|".join(SALARY_PATTERNS)
    severance_pattern = "|".join(SEVERANCE_PATTERNS)
    
    sueldos_mask = base_masks["gastos_admin"] & data.eri["Display Name"].str.contains(salary_pattern, case=False, na=False)
    cesantias_mask = base_masks["gastos_admin"] & data.eri["Display Name"].str.contains(severance_pattern, case=False, na=False)
    extra_masks = {
        "sueldos": sueldos_mask,
        "cesantias": cesantias_mask,
    }

    current_col = data.current_month_col
    gastos_values = {
        name: abs(float(data.eri.loc[mask, current_col].sum()))
        for name, mask in base_masks.items()
    }
    extra_values = {
        name: abs(float(data.eri.loc[mask, current_col].sum()))
        for name, mask in extra_masks.items()
    }
    
    return gastos_values, extra_values


def _build_budget_summary(
    data: FinancialData, 
    config: AppConfig, 
    actual_ingresos: float, 
    actual_total_gastos: float,
    gastos_values: dict[str, float]
) -> pd.DataFrame:
    """Build budget execution summary table.
    
    Args:
        data: Financial data
        config: Application configuration
        actual_ingresos: Actual income amount
        actual_total_gastos: Total actual expenses
        gastos_values: Categorized expense values
        
    Returns:
        Summary DataFrame
    """
    # Calculate budget execution percentages
    ejecutado_ingresos_pct = (
        (actual_ingresos / config.budgets.ingresos_mensual) * 100
        if config.budgets.ingresos_mensual > 0
        else 0
    )
    ejecutado_gastos_pct = (
        (actual_total_gastos / config.budgets.gastos_mensual) * 100
        if config.budgets.gastos_mensual > 0
        else 0
    )

    # Enhanced summary with more detailed breakdown
    summary_data = [
        ["Ingresos", actual_ingresos, config.budgets.ingresos_mensual, ejecutado_ingresos_pct],
        ["Gastos Totales", actual_total_gastos, config.budgets.gastos_mensual, ejecutado_gastos_pct],
        ["Gastos Administrativos", gastos_values["gastos_admin"], 0, 0],
        ["Gastos Otros", gastos_values["gastos_otros"], 0, 0],
        ["Costos de Venta", gastos_values["costos_venta"], 0, 0],
        ["Costos de Producción", gastos_values["costos_prod"], 0, 0],
    ]

    return pd.DataFrame(
        summary_data,
        columns=["Categoría", f"Actual {data.current_month}", "Presupuesto Mensual", "% Ejecutado"]
    )


def _build_expense_distribution(
    data: FinancialData, 
    base_masks: dict[str, pd.Series], 
    extra_masks: dict[str, pd.Series],
    actual_total_gastos: float
) -> pd.DataFrame:
    """Build expense distribution analysis.
    
    Args:
        data: Financial data
        base_masks: Base expense category masks
        extra_masks: Additional expense category masks
        actual_total_gastos: Total actual expenses
        
    Returns:
        Distribution analysis DataFrame
    """
    if not actual_total_gastos:
        return pd.DataFrame()
    
    months = list(data.months)
    current_col = data.current_month_col
    previous_index = max(months.index(current_col) - 1, 0)
    previous_month = months[previous_index]
    
    relevant_mask = np.logical_or.reduce(tuple(base_masks.values()) + tuple(extra_masks.values()))
    distribution = data.eri.loc[relevant_mask, ["Display Name"] + months].copy()
    distribution.set_index("Display Name", inplace=True)
    distribution[months] = distribution[months].abs()
    distribution["Average Jan-Current"] = distribution[months].mean(axis=1)
    distribution[f"% Diff vs {previous_month.split()[0]}"] = (
        (
            distribution[current_col] - distribution[previous_month]
        )
        / distribution[previous_month].replace(0, np.nan)
    ).fillna(0) * 100
    distribution["% vs Average"] = (
        (
            distribution[current_col] - distribution["Average Jan-Current"]
        )
        / distribution["Average Jan-Current"].replace(0, np.nan)
    ).fillna(0) * 100
    distribution[f"% del Total {data.current_month}"] = (
        distribution[current_col] / actual_total_gastos * 100
    )
    
    return distribution


def compute_budget_execution(data: FinancialData, config: AppConfig) -> BudgetResult:
    """Calculate budget execution analysis.
    
    Args:
        data: Financial data containing income statement and ERI
        config: Application configuration with budget settings
        
    Returns:
        BudgetResult with summary and distribution analysis
    """
    # Get income from income statement
    actual_ingresos = _calculate_income(data)

    # Categorize expenses
    gastos_values, extra_values = _categorize_expenses(data)
    actual_total_gastos = sum(gastos_values.values())

    # Build summary table
    summary = _build_budget_summary(data, config, actual_ingresos, actual_total_gastos, gastos_values)

    # Build expense distribution analysis
    base_masks = {
        "gastos_admin": data.eri["Codigo"].str.match(ADMIN_EXPENSES_PATTERN, na=False),
        "gastos_otros": data.eri["Codigo"].str.match(OTHER_EXPENSES_PATTERN, na=False),
        "costos_venta": data.eri["Codigo"].str.match(SALES_COSTS_PATTERN, na=False),
        "costos_prod": data.eri["Codigo"].str.match(PRODUCTION_COSTS_PATTERN, na=False),
    }
    
    salary_pattern = "|".join(SALARY_PATTERNS)
    severance_pattern = "|".join(SEVERANCE_PATTERNS)
    
    extra_masks = {
        "sueldos": base_masks["gastos_admin"] & data.eri["Display Name"].str.contains(salary_pattern, case=False, na=False),
        "cesantias": base_masks["gastos_admin"] & data.eri["Display Name"].str.contains(severance_pattern, case=False, na=False),
    }
    
    distribution = _build_expense_distribution(data, base_masks, extra_masks, actual_total_gastos)

    return BudgetResult(
        summary=summary,
        distribution=distribution,
        gastos_admin=gastos_values["gastos_admin"],
        gastos_otros=gastos_values["gastos_otros"],
        costos_venta=gastos_values["costos_venta"],
        costos_produccion=gastos_values["costos_prod"],
    )


def _sum_for_balance(balance: pd.DataFrame, level: str, codes: Sequence[str]) -> float:
    """Sum balance sheet values for specific level and codes.
    
    Args:
        balance: Balance sheet DataFrame
        level: Account level (Clase, Grupo, etc.)
        codes: List of account codes to sum
        
    Returns:
        Sum of balance values
    """
    frame = balance[(balance["Nivel"] == level) & balance["Código cuenta contable"].isin(codes)]
    return float(frame["Saldo final"].sum()) if not frame.empty else 0.0


def _get_income_statement_data(resultado: pd.DataFrame, current_col: str) -> tuple[float, float, float]:
    """Extract key values from income statement.
    
    Args:
        resultado: Income statement DataFrame
        current_col: Current month column name
        
    Returns:
        Tuple of (costs, profit, income)
    """
    costos_series = resultado[
        resultado["Descripcion"].str.contains(COST_DESCRIPTION, case=False, na=False)
    ][current_col]
    utilidad_series = resultado[
        resultado["Descripcion"].str.contains(PROFIT_DESCRIPTION, case=False, na=False)
    ][current_col]
    ingresos_series = resultado[
        resultado["Descripcion"].str.contains(INCOME_DESCRIPTION, case=False, na=False)
    ][current_col]

    costos = abs(float(costos_series.max())) if not costos_series.empty else 0.0
    utilidad = float(utilidad_series.max()) if not utilidad_series.empty else 0.0
    ingresos = abs(float(ingresos_series.max())) if not ingresos_series.empty else 0.0
    
    return costos, utilidad, ingresos


def _calculate_ebitda_components(data: FinancialData) -> tuple[float, float]:
    """Calculate depreciation and interest for EBITDA calculation.
    
    Args:
        data: Financial data containing ERI
        
    Returns:
        Tuple of (depreciation, interest)
    """
    # Depreciation: filter by account name containing "DEPRECIACION" or "AMORTIZACION"
    depreciation_pattern = "|".join(DEPRECIATION_PATTERNS)
    depreciacion_mask = data.eri["Display Name"].str.contains(
        depreciation_pattern, case=False, na=False
    )
    depreciacion = abs(float(data.eri.loc[depreciacion_mask, data.current_month_col].sum()))
    
    # Interest expenses: filter by account name containing "INTERES"
    interest_pattern = "|".join(INTEREST_PATTERNS)
    intereses_mask = data.eri["Display Name"].str.contains(
        interest_pattern, case=False, na=False
    )
    intereses = abs(float(data.eri.loc[intereses_mask, data.current_month_col].sum()))
    
    return depreciacion, intereses


def _calculate_financial_ratios(
    current_assets: float,
    current_liabilities: float,
    inventories: float,
    equity: float,
    ingresos: float,
    costos: float,
    utilidad: float
) -> dict[str, float]:
    """Calculate all financial ratios with division by zero protection.
    
    Args:
        current_assets: Current assets amount
        current_liabilities: Current liabilities amount
        inventories: Inventories amount
        equity: Equity amount
        ingresos: Income amount
        costos: Costs amount
        utilidad: Profit amount
        
    Returns:
        Dictionary of calculated ratios
    """
    # Liquidity ratios
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0.0
    quick_ratio = (
        (current_assets - inventories) / current_liabilities if current_liabilities > 0 else 0.0
    )
    
    # Profitability ratios
    margen_bruto = (
        ((ingresos - costos) / ingresos) * 100 if ingresos > 0 else 0.0
    )
    margen_neto = (utilidad / ingresos * 100) if ingresos > 0 else 0.0
    roe = (utilidad / equity * 100) if equity > 0 else 0.0
    
    # Leverage ratios
    deuda_patrimonio = current_liabilities / equity if equity > 0 else 0.0
    
    # Activity ratios
    rotacion_inventarios = costos / inventories if inventories > 0 else 0.0
    
    return {
        "Current Ratio": round(current_ratio, 2),
        "Quick Ratio": round(quick_ratio, 2),
        "Margen Bruto %": round(margen_bruto, 2),
        "Margen Neto %": round(margen_neto, 2),
        "ROE %": round(roe, 2),
        "Deuda/Patrimonio": round(deuda_patrimonio, 2),
        "Rotación Inventarios": round(rotacion_inventarios, 2),
    }


def compute_kpis(data: FinancialData, budget: BudgetResult) -> KPIResult:
    """Calculate comprehensive financial KPIs.
    
    Args:
        data: Financial data containing balance sheet and income statement
        budget: Budget execution results with categorized expenses
        
    Returns:
        KPIResult containing calculated metrics table and dictionary
    """
    balance = data.balance
    resultado = data.resultado

    # Get assets, liabilities, and equity from Clase level
    total_assets = _sum_for_balance(balance, "Clase", [ASSET_CLASS_CODE])
    current_assets = _sum_for_balance(balance, "Grupo", CURRENT_ASSET_GROUPS)
    inventories = _sum_for_balance(balance, "Grupo", [INVENTORY_GROUP_CODE])
    current_liabilities = abs(_sum_for_balance(balance, "Clase", [LIABILITY_CLASS_CODE]))
    equity = abs(_sum_for_balance(balance, "Clase", [EQUITY_CLASS_CODE])) or max(total_assets - current_liabilities, 0)

    # Get income statement data
    costos, utilidad, ingresos = _get_income_statement_data(resultado, data.resultado_current_col)

    # Calculate EBITDA components
    depreciacion, intereses = _calculate_ebitda_components(data)
    
    # Calculate financial ratios
    ratios = _calculate_financial_ratios(
        current_assets, current_liabilities, inventories, equity, 
        ingresos, costos, utilidad
    )
    
    # Add EBITDA to ratios
    ebitda = utilidad + depreciacion + intereses
    ratios["EBITDA"] = round(ebitda, 2)

    # Create results table
    table = pd.DataFrame(
        {
            "KPI": list(ratios.keys()),
            f"Valor {data.current_month} 2025": list(ratios.values()),
        }
    )

    return KPIResult(table=table, metrics=ratios)


def compute_ai_enhanced_analysis(data: FinancialData, budget: BudgetResult, kpis: KPIResult, config: AppConfig):
    """Compute AI-enhanced financial analysis using Ollama.
    
    Args:
        data: Financial data
        budget: Budget execution results
        kpis: KPI results
        config: Application configuration
        
    Returns:
        AIInsights object with enhanced analysis
    """
    if not config.ollama.enabled:
        # Return basic insights if AI is disabled
        from .ai_analyzer import AIInsights
        return AIInsights(
            executive_summary=f"Financial analysis for {data.current_month} 2025 completed.",
            key_insights=["Standard financial analysis completed."],
            risk_assessment="Basic risk assessment applied.",
            recommendations=["Continue monitoring financial performance."],
            trend_analysis="Basic trend analysis completed.",
            budget_analysis="Budget execution analysis completed.",
            kpi_analysis="KPI analysis completed."
        )
    
    try:
        from .ai_analyzer import FinancialAIAnalyzer
        analyzer = FinancialAIAnalyzer(config, model=config.ollama.model)
        return analyzer.analyze_financials(data, budget, kpis)
    except Exception as e:
        # Fallback to basic analysis if AI fails
        from .ai_analyzer import AIInsights
        return AIInsights(
            executive_summary=f"Financial analysis for {data.current_month} 2025 completed (AI unavailable).",
            key_insights=["Standard financial analysis completed."],
            risk_assessment="Basic risk assessment applied.",
            recommendations=["Continue monitoring financial performance."],
            trend_analysis="Basic trend analysis completed.",
            budget_analysis="Budget execution analysis completed.",
            kpi_analysis="KPI analysis completed."
        )

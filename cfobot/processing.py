"""Core financial processing logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .config import AppConfig
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


def compute_budget_execution(data: FinancialData, config: AppConfig) -> BudgetResult:
    # Get income from income statement
    ingresos_series = data.resultado[
        data.resultado["Descripcion"].str.contains("INGRESOS ORDINARIOS", case=False, na=False)
    ][data.resultado_current_col]
    actual_ingresos = abs(float(ingresos_series.iloc[0])) if not ingresos_series.empty else 0.0

    # Enhanced expense categorization with better mapping
    base_masks = {
        "gastos_admin": data.eri["Codigo"].str.match(r"^51[0-9]{4,}", na=False),
        "gastos_otros": data.eri["Codigo"].str.match(r"^53[0-9]{4,}", na=False),
        "costos_venta": data.eri["Codigo"].str.match(r"^61[0-9]{4,}", na=False),
        "costos_prod": data.eri["Codigo"].str.match(r"^(72|73)[0-9]{4,}", na=False),
    }

    sueldos_mask = base_masks["gastos_admin"] & data.eri["Display Name"].str.contains("SUELDO|SALARIO", case=False, na=False)
    cesantias_mask = base_masks["gastos_admin"] & data.eri["Display Name"].str.contains("CESANTIA", case=False, na=False)
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
    actual_total_gastos = sum(gastos_values.values())

    # Calculate budget execution percentages
    ejecutado_ingresos_pct = (
        (actual_ingresos / config.budgets.ingresos_mensual) * 100
        if config.budgets.ingresos_mensual
        else 0
    )
    ejecutado_gastos_pct = (
        (actual_total_gastos / config.budgets.gastos_mensual) * 100
        if config.budgets.gastos_mensual
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

    summary = pd.DataFrame(
        summary_data,
        columns=["Categoría", f"Actual {data.current_month}", "Presupuesto Mensual", "% Ejecutado"]
    )

    # Enhanced distribution analysis
    distribution = pd.DataFrame()
    if actual_total_gastos:
        months = list(data.months)
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

    return BudgetResult(
        summary=summary,
        distribution=distribution,
        gastos_admin=gastos_values["gastos_admin"],
        gastos_otros=gastos_values["gastos_otros"],
        costos_venta=gastos_values["costos_venta"],
        costos_produccion=gastos_values["costos_prod"],
    )


def compute_kpis(data: FinancialData, budget: BudgetResult) -> KPIResult:
    balance = data.balance
    resultado = data.resultado

    def _sum_for(level: str, codes: Sequence[str]) -> float:
        frame = balance[(balance["Nivel"] == level) & balance["Código cuenta contable"].isin(codes)]
        return float(frame["Saldo final"].sum()) if not frame.empty else 0.0

    # Get assets, liabilities, and equity from Clase level
    total_assets = _sum_for("Clase", ["1"])
    current_assets = _sum_for("Grupo", ["11", "12", "13", "14"])
    inventories = _sum_for("Grupo", ["14"])
    current_liabilities = abs(_sum_for("Clase", ["2"]))
    equity = abs(_sum_for("Clase", ["3"])) or max(total_assets - current_liabilities, 0)

    # Get income statement data
    costos_series = resultado[
        resultado["Descripcion"].str.contains("COSTO DE VENTA", case=False, na=False)
    ][data.resultado_current_col]
    utilidad_series = resultado[
        resultado["Descripcion"].str.contains("RESULTADO DEL EJERCICIO", case=False, na=False)
    ][data.resultado_current_col]

    costos = abs(float(costos_series.max())) if not costos_series.empty else 0.0
    utilidad = float(utilidad_series.max()) if not utilidad_series.empty else 0.0

    # Enhanced EBITDA calculation - get depreciation and interest from ERI
    # Depreciation typically in 51xxxx accounts (administrative expenses)
    depreciacion_mask = data.eri["Codigo"].str.match(r"^51[0-9]{4}", na=False)
    depreciacion = abs(float(data.eri.loc[depreciacion_mask, data.current_month_col].sum()))
    
    # Interest expenses typically in 53xxxx accounts
    intereses_mask = data.eri["Codigo"].str.match(r"^53[0-9]{4}", na=False)
    intereses = abs(float(data.eri.loc[intereses_mask, data.current_month_col].sum()))

    ingresos_actual = abs(float(budget.summary.loc[0, f"Actual {data.current_month}"]))
    
    # Calculate financial ratios
    current_ratio = current_assets / current_liabilities if current_liabilities else 0.0
    quick_ratio = (
        (current_assets - inventories) / current_liabilities if current_liabilities else 0.0
    )
    margen_bruto = (
        ((ingresos_actual - costos) / ingresos_actual) * 100 if ingresos_actual else 0.0
    )
    margen_neto = (utilidad / ingresos_actual * 100) if ingresos_actual else 0.0
    roe = (utilidad / equity * 100) if equity else 0.0
    deuda_patrimonio = current_liabilities / equity if equity else 0.0
    rotacion_inventarios = costos / inventories if inventories else 0.0
    
    # Enhanced EBITDA calculation: utilidad + depreciación + intereses
    ebitda = utilidad + depreciacion + intereses

    metrics = {
        "Current Ratio": round(current_ratio, 2),
        "Quick Ratio": round(quick_ratio, 2),
        "Margen Bruto %": round(margen_bruto, 2),
        "Margen Neto %": round(margen_neto, 2),
        "ROE %": round(roe, 2),
        "Deuda/Patrimonio": round(deuda_patrimonio, 2),
        "Rotación Inventarios": round(rotacion_inventarios, 2),
        "EBITDA": round(ebitda, 2),
    }

    table = pd.DataFrame(
        {
            "KPI": list(metrics.keys()),
            f"Valor {data.current_month} 2025": list(metrics.values()),
        }
    )

    return KPIResult(table=table, metrics=metrics)

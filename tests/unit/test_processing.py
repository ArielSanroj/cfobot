"""Unit tests for processing module."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock

from cfobot.processing import (
    _calculate_income,
    _categorize_expenses,
    _build_budget_summary,
    _build_expense_distribution,
    _sum_for_balance,
    _get_income_statement_data,
    _calculate_ebitda_components,
    _calculate_financial_ratios,
    compute_budget_execution,
    compute_kpis,
    BudgetResult,
    KPIResult,
)
from cfobot.data_loader import FinancialData
from cfobot.config import AppConfig, BudgetConfig


@pytest.fixture
def sample_financial_data():
    """Create sample financial data for testing."""
    # Sample income statement
    resultado_data = {
        'Descripcion': ['INGRESOS ORDINARIOS', 'COSTO DE VENTA', 'RESULTADO DEL EJERCICIO'],
        'Total MARZO': [120000000, 30000000, 15000000]
    }
    resultado_df = pd.DataFrame(resultado_data)
    
    # Sample ERI data
    eri_data = {
        'Codigo': ['510101', '510201', '530101', '610101', '720101'],
        'Nombre': ['SUELDOS ADMINISTRATIVOS', 'CESANTIAS', 'INTERESES', 'COSTO VENTAS', 'COSTO PRODUCCION'],
        'Display Name': ['SUELDOS ADMINISTRATIVOS', 'CESANTIAS', 'INTERESES', 'COSTO VENTAS', 'COSTO PRODUCCION'],
        'MARZO DE 2025': [50000000, 10000000, 5000000, 30000000, 40000000]
    }
    eri_df = pd.DataFrame(eri_data)
    
    # Sample balance sheet
    balance_data = {
        'Nivel': ['Clase', 'Clase', 'Clase', 'Grupo', 'Grupo', 'Grupo', 'Grupo'],
        'Código cuenta contable': ['1', '2', '3', '11', '12', '13', '14'],
        'Nombre cuenta contable': ['ACTIVO', 'PASIVO', 'PATRIMONIO', 'ACTIVO CORRIENTE', 'INVERSIONES', 'CUENTAS POR COBRAR', 'INVENTARIOS'],
        'Saldo final': [500000000, 200000000, 300000000, 150000000, 50000000, 80000000, 120000000]
    }
    balance_df = pd.DataFrame(balance_data)
    
    # Sample caratula
    caratula_df = pd.DataFrame({
        'Column_0': ['Diferencia'],
        'Column_1': [5000000]
    })
    
    # Mock workbook
    mock_workbook = Mock()
    mock_workbook.sheet_names = ['BALANCE MARZO', 'INFORME-ERI', 'ESTADO RESULTADO', 'CARATULA']
    
    return FinancialData(
        current_month='MARZO',
        current_month_col='MARZO DE 2025',
        resultado_current_col='Total MARZO',
        balance=balance_df,
        eri=eri_df,
        resultado=resultado_df,
        caratula=caratula_df,
        months=['ENERO DE 2025', 'FEBRERO DE 2025', 'MARZO DE 2025'],
        workbook=mock_workbook
    )


@pytest.fixture
def sample_config():
    """Create sample configuration for testing."""
    return AppConfig(
        budgets=BudgetConfig(ingresos_mensual=100_000_000, gastos_mensual=125_000_000)
    )


class TestCalculateIncome:
    """Test income calculation function."""
    
    def test_calculate_income_success(self, sample_financial_data):
        """Test successful income calculation."""
        income = _calculate_income(sample_financial_data)
        assert income == 120000000.0
    
    def test_calculate_income_empty_series(self, sample_financial_data):
        """Test income calculation with empty series."""
        sample_financial_data.resultado = pd.DataFrame({
            'Descripcion': ['OTHER ITEM'],
            'Total MARZO': [1000000]
        })
        income = _calculate_income(sample_financial_data)
        assert income == 0.0


class TestCategorizeExpenses:
    """Test expense categorization function."""
    
    def test_categorize_expenses_success(self, sample_financial_data):
        """Test successful expense categorization."""
        gastos_values, extra_values = _categorize_expenses(sample_financial_data)
        
        # Check base expenses
        assert gastos_values['gastos_admin'] == 50000000.0  # SUELDOS ADMINISTRATIVOS
        assert gastos_values['gastos_otros'] == 5000000.0   # INTERESES
        assert gastos_values['costos_venta'] == 30000000.0 # COSTO VENTAS
        assert gastos_values['costos_prod'] == 40000000.0  # COSTO PRODUCCION
        
        # Check extra expenses
        assert extra_values['sueldos'] == 50000000.0  # SUELDOS ADMINISTRATIVOS
        assert extra_values['cesantias'] == 10000000.0  # CESANTIAS


class TestBuildBudgetSummary:
    """Test budget summary building function."""
    
    def test_build_budget_summary_success(self, sample_financial_data, sample_config):
        """Test successful budget summary creation."""
        actual_ingresos = 120000000.0
        actual_total_gastos = 125000000.0
        gastos_values = {
            'gastos_admin': 50000000.0,
            'gastos_otros': 5000000.0,
            'costos_venta': 30000000.0,
            'costos_prod': 40000000.0
        }
        
        summary = _build_budget_summary(
            sample_financial_data, sample_config, 
            actual_ingresos, actual_total_gastos, gastos_values
        )
        
        assert len(summary) == 6
        assert summary.iloc[0]['Categoría'] == 'Ingresos'
        assert summary.iloc[0][f'Actual {sample_financial_data.current_month}'] == 120000000.0
        assert summary.iloc[0]['% Ejecutado'] == 120.0  # 120M / 100M * 100


class TestSumForBalance:
    """Test balance sheet summation function."""
    
    def test_sum_for_balance_success(self, sample_financial_data):
        """Test successful balance sheet summation."""
        total_assets = _sum_for_balance(sample_financial_data.balance, "Clase", ["1"])
        assert total_assets == 500000000.0
        
        current_assets = _sum_for_balance(sample_financial_data.balance, "Grupo", ["11", "12", "13", "14"])
        assert current_assets == 400000000.0  # 150M + 50M + 80M + 120M
    
    def test_sum_for_balance_empty_result(self, sample_financial_data):
        """Test balance sheet summation with no matching records."""
        result = _sum_for_balance(sample_financial_data.balance, "Clase", ["999"])
        assert result == 0.0


class TestGetIncomeStatementData:
    """Test income statement data extraction."""
    
    def test_get_income_statement_data_success(self, sample_financial_data):
        """Test successful income statement data extraction."""
        costos, utilidad, ingresos = _get_income_statement_data(
            sample_financial_data.resultado, sample_financial_data.resultado_current_col
        )
        
        assert costos == 30000000.0
        assert utilidad == 15000000.0
        assert ingresos == 120000000.0
    
    def test_get_income_statement_data_missing_data(self):
        """Test income statement data extraction with missing data."""
        empty_df = pd.DataFrame({'Descripcion': [], 'Total MARZO': []})
        costos, utilidad, ingresos = _get_income_statement_data(empty_df, 'Total MARZO')
        
        assert costos == 0.0
        assert utilidad == 0.0
        assert ingresos == 0.0


class TestCalculateEbitdaComponents:
    """Test EBITDA components calculation."""
    
    def test_calculate_ebitda_components_success(self, sample_financial_data):
        """Test successful EBITDA components calculation."""
        depreciacion, intereses = _calculate_ebitda_components(sample_financial_data)
        
        # Should find INTERESES in the ERI data
        assert intereses == 5000000.0
        # No depreciation accounts in sample data
        assert depreciacion == 0.0


class TestCalculateFinancialRatios:
    """Test financial ratios calculation."""
    
    def test_calculate_financial_ratios_success(self):
        """Test successful financial ratios calculation."""
        ratios = _calculate_financial_ratios(
            current_assets=400000000.0,
            current_liabilities=200000000.0,
            inventories=120000000.0,
            equity=300000000.0,
            ingresos=120000000.0,
            costos=30000000.0,
            utilidad=15000000.0
        )
        
        assert ratios['Current Ratio'] == 2.0  # 400M / 200M
        assert ratios['Quick Ratio'] == 1.4   # (400M - 120M) / 200M
        assert ratios['Margen Bruto %'] == 75.0  # (120M - 30M) / 120M * 100
        assert ratios['Margen Neto %'] == 12.5   # 15M / 120M * 100
        assert ratios['ROE %'] == 5.0            # 15M / 300M * 100
        assert ratios['Deuda/Patrimonio'] == 0.67  # 200M / 300M
        assert ratios['Rotación Inventarios'] == 0.25  # 30M / 120M
    
    def test_calculate_financial_ratios_division_by_zero(self):
        """Test financial ratios calculation with division by zero."""
        ratios = _calculate_financial_ratios(
            current_assets=0.0,
            current_liabilities=0.0,
            inventories=0.0,
            equity=0.0,
            ingresos=0.0,
            costos=0.0,
            utilidad=0.0
        )
        
        # All ratios should be 0.0 when denominators are 0
        for ratio_name, value in ratios.items():
            assert value == 0.0, f"{ratio_name} should be 0.0"


class TestComputeBudgetExecution:
    """Test budget execution computation."""
    
    def test_compute_budget_execution_success(self, sample_financial_data, sample_config):
        """Test successful budget execution computation."""
        result = compute_budget_execution(sample_financial_data, sample_config)
        
        assert isinstance(result, BudgetResult)
        assert len(result.summary) == 6
        assert result.gastos_admin == 50000000.0
        assert result.gastos_otros == 5000000.0
        assert result.costos_venta == 30000000.0
        assert result.costos_produccion == 40000000.0


class TestComputeKpis:
    """Test KPI computation."""
    
    def test_compute_kpis_success(self, sample_financial_data):
        """Test successful KPI computation."""
        # Create a budget result for KPI calculation
        budget_result = BudgetResult(
            summary=pd.DataFrame({
                'Categoría': ['Ingresos'],
                'Actual MARZO': [120000000.0],
                'Presupuesto Mensual': [100000000.0],
                '% Ejecutado': [120.0]
            }),
            distribution=pd.DataFrame(),
            gastos_admin=50000000.0,
            gastos_otros=5000000.0,
            costos_venta=30000000.0,
            costos_produccion=40000000.0
        )
        
        result = compute_kpis(sample_financial_data, budget_result)
        
        assert isinstance(result, KPIResult)
        assert len(result.table) == 8  # 7 ratios + EBITDA
        assert 'Current Ratio' in result.metrics
        assert 'EBITDA' in result.metrics
        assert result.metrics['Current Ratio'] == 2.0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_dataframes(self):
        """Test functions with empty DataFrames."""
        empty_data = FinancialData(
            current_month='MARZO',
            current_month_col='MARZO DE 2025',
            resultado_current_col='Total MARZO',
            balance=pd.DataFrame(),
            eri=pd.DataFrame(),
            resultado=pd.DataFrame(),
            caratula=pd.DataFrame(),
            months=[],
            workbook=Mock()
        )
        
        config = AppConfig()
        
        # Should not raise exceptions
        budget_result = compute_budget_execution(empty_data, config)
        assert isinstance(budget_result, BudgetResult)
        
        kpi_result = compute_kpis(empty_data, budget_result)
        assert isinstance(kpi_result, KPIResult)
    
    def test_negative_values(self, sample_financial_data):
        """Test handling of negative values."""
        # Modify data to include negative values
        sample_financial_data.resultado.loc[0, 'Total MARZO'] = -120000000.0
        
        income = _calculate_income(sample_financial_data)
        assert income == 120000000.0  # Should be absolute value

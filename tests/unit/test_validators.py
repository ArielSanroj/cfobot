"""Unit tests for validators module."""

import pytest
import pandas as pd
import numpy as np

from cfobot.validators import (
    sanitize_filename_component,
    validate_month_name,
    validate_balance_equation,
    detect_outliers,
    validate_account_signs,
    validate_financial_ratios,
    validate_file_path,
    validate_data_types,
    sanitize_dataframe,
)


class TestSanitizeFilenameComponent:
    """Test filename component sanitization."""
    
    def test_sanitize_normal_component(self):
        """Test sanitization of normal filename component."""
        result = sanitize_filename_component("MARZO")
        assert result == "MARZO"
    
    def test_sanitize_path_traversal(self):
        """Test sanitization of path traversal attempts."""
        result = sanitize_filename_component("../../../etc/passwd")
        assert result == "etcpasswd"
    
    def test_sanitize_dangerous_characters(self):
        """Test sanitization of dangerous characters."""
        result = sanitize_filename_component("test<>:\"|?*")
        assert result == "test"
    
    def test_sanitize_long_string(self):
        """Test sanitization of long strings."""
        long_string = "A" * 100
        result = sanitize_filename_component(long_string)
        assert len(result) == 50
    
    def test_sanitize_non_string(self):
        """Test sanitization of non-string input."""
        result = sanitize_filename_component(123)
        assert result == "123"


class TestValidateMonthName:
    """Test month name validation."""
    
    def test_validate_canonical_month(self):
        """Test validation of canonical month names."""
        assert validate_month_name("MARZO") == "MARZO"
        assert validate_month_name("ENERO") == "ENERO"
    
    def test_validate_month_alias(self):
        """Test validation of month aliases."""
        assert validate_month_name("MAR") == "MARZO"
        assert validate_month_name("ENE") == "ENERO"
        assert validate_month_name("DIC") == "DICIEMBRE"
    
    def test_validate_case_insensitive(self):
        """Test case insensitive validation."""
        assert validate_month_name("marzo") == "MARZO"
        assert validate_month_name("Marzo") == "MARZO"
    
    def test_validate_invalid_month(self):
        """Test validation of invalid month names."""
        with pytest.raises(ValueError):
            validate_month_name("INVALID")
        
        with pytest.raises(ValueError):
            validate_month_name("")
    
    def test_validate_non_string(self):
        """Test validation of non-string input."""
        with pytest.raises(ValueError):
            validate_month_name(123)


class TestValidateBalanceEquation:
    """Test balance equation validation."""
    
    def test_validate_balanced_equation(self):
        """Test validation of balanced equation."""
        df = pd.DataFrame({
            'Nivel': ['Clase', 'Clase', 'Clase'],
            'Código cuenta contable': ['1', '2', '3'],
            'Saldo final': [1000, 600, 400]
        })
        assert validate_balance_equation(df) is True
    
    def test_validate_unbalanced_equation(self):
        """Test validation of unbalanced equation."""
        df = pd.DataFrame({
            'Nivel': ['Clase', 'Clase', 'Clase'],
            'Código cuenta contable': ['1', '2', '3'],
            'Saldo final': [1000, 600, 300]  # 1000 != 600 + 300
        })
        assert validate_balance_equation(df) is False
    
    def test_validate_small_difference(self):
        """Test validation with small rounding difference."""
        df = pd.DataFrame({
            'Nivel': ['Clase', 'Clase', 'Clase'],
            'Código cuenta contable': ['1', '2', '3'],
            'Saldo final': [1000, 600, 399.5]  # 0.5 difference
        })
        assert validate_balance_equation(df) is True
    
    def test_validate_empty_dataframe(self):
        """Test validation with empty DataFrame."""
        df = pd.DataFrame()
        assert validate_balance_equation(df) is False


class TestDetectOutliers:
    """Test outlier detection."""
    
    def test_detect_outliers_normal_data(self):
        """Test outlier detection with normal data."""
        series = pd.Series([100, 105, 98, 102, 103])
        outliers = detect_outliers(series)
        assert outliers.sum() == 0
    
    def test_detect_outliers_with_outlier(self):
        """Test outlier detection with outlier."""
        series = pd.Series([100, 105, 98, 1000, 102])
        outliers = detect_outliers(series)
        assert outliers.sum() == 1
        assert outliers.iloc[3] is True
    
    def test_detect_outliers_small_series(self):
        """Test outlier detection with small series."""
        series = pd.Series([100, 105])
        outliers = detect_outliers(series)
        assert outliers.sum() == 0
    
    def test_detect_outliers_zero_std(self):
        """Test outlier detection with zero standard deviation."""
        series = pd.Series([100, 100, 100])
        outliers = detect_outliers(series)
        assert outliers.sum() == 0


class TestValidateAccountSigns:
    """Test account signs validation."""
    
    def test_validate_correct_signs(self):
        """Test validation with correct account signs."""
        df = pd.DataFrame({
            'Nivel': ['Clase', 'Clase', 'Clase'],
            'Código cuenta contable': ['1', '2', '3'],
            'Nombre cuenta contable': ['ACTIVO', 'PASIVO', 'PATRIMONIO'],
            'Saldo final': [1000, -600, -400]  # Assets positive, liabilities/equity negative
        })
        issues = validate_account_signs(df)
        assert len(issues['negative_assets']) == 0
        assert len(issues['positive_liabilities']) == 0
        assert len(issues['negative_equity']) == 0
    
    def test_validate_negative_assets(self):
        """Test validation with negative assets."""
        df = pd.DataFrame({
            'Nivel': ['Clase'],
            'Código cuenta contable': ['1'],
            'Nombre cuenta contable': ['ACTIVO'],
            'Saldo final': [-1000]  # Negative asset
        })
        issues = validate_account_signs(df)
        assert len(issues['negative_assets']) == 1
        assert issues['negative_assets'][0] == 'ACTIVO'
    
    def test_validate_positive_liabilities(self):
        """Test validation with positive liabilities."""
        df = pd.DataFrame({
            'Nivel': ['Clase'],
            'Código cuenta contable': ['2'],
            'Nombre cuenta contable': ['PASIVO'],
            'Saldo final': [600]  # Positive liability
        })
        issues = validate_account_signs(df)
        assert len(issues['positive_liabilities']) == 1
        assert issues['positive_liabilities'][0] == 'PASIVO'


class TestValidateFinancialRatios:
    """Test financial ratios validation."""
    
    def test_validate_normal_ratios(self):
        """Test validation with normal ratios."""
        ratios = {
            'Current Ratio': 2.0,
            'Margen Neto %': 10.0,
            'Deuda/Patrimonio': 1.0
        }
        warnings = validate_financial_ratios(ratios)
        assert len(warnings['liquidity_warnings']) == 0
        assert len(warnings['profitability_warnings']) == 0
        assert len(warnings['leverage_warnings']) == 0
    
    def test_validate_low_liquidity(self):
        """Test validation with low liquidity."""
        ratios = {
            'Current Ratio': 0.8,  # Below 1.0
            'Margen Neto %': 10.0,
            'Deuda/Patrimonio': 1.0
        }
        warnings = validate_financial_ratios(ratios)
        assert len(warnings['liquidity_warnings']) == 1
        assert 'liquidity issues' in warnings['liquidity_warnings'][0]
    
    def test_validate_negative_margin(self):
        """Test validation with negative margin."""
        ratios = {
            'Current Ratio': 2.0,
            'Margen Neto %': -5.0,  # Negative margin
            'Deuda/Patrimonio': 1.0
        }
        warnings = validate_financial_ratios(ratios)
        assert len(warnings['profitability_warnings']) == 1
        assert 'Negative net margin' in warnings['profitability_warnings'][0]
    
    def test_validate_high_leverage(self):
        """Test validation with high leverage."""
        ratios = {
            'Current Ratio': 2.0,
            'Margen Neto %': 10.0,
            'Deuda/Patrimonio': 3.0  # Above 2.0
        }
        warnings = validate_financial_ratios(ratios)
        assert len(warnings['leverage_warnings']) == 1
        assert 'high leverage' in warnings['leverage_warnings'][0]


class TestValidateFilePath:
    """Test file path validation."""
    
    def test_validate_existing_file(self, tmp_path):
        """Test validation of existing file."""
        test_file = tmp_path / "test.xlsx"
        test_file.touch()
        
        result = validate_file_path(test_file)
        assert result is True
    
    def test_validate_nonexistent_file(self, tmp_path):
        """Test validation of non-existent file."""
        test_file = tmp_path / "nonexistent.xlsx"
        
        with pytest.raises(ValueError):
            validate_file_path(test_file)
    
    def test_validate_path_traversal(self, tmp_path):
        """Test validation with path traversal."""
        test_file = tmp_path / "../../../etc/passwd"
        
        with pytest.raises(ValueError):
            validate_file_path(test_file)
    
    def test_validate_wrong_extension(self, tmp_path):
        """Test validation with wrong file extension."""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        with pytest.raises(ValueError):
            validate_file_path(test_file)


class TestValidateDataTypes:
    """Test data type validation."""
    
    def test_validate_correct_types(self):
        """Test validation with correct data types."""
        df = pd.DataFrame({
            'amount': [100, 200, 300],
            'description': ['A', 'B', 'C']
        })
        expected_types = {'amount': float, 'description': str}
        errors = validate_data_types(df, expected_types)
        assert len(errors) == 0
    
    def test_validate_missing_column(self):
        """Test validation with missing column."""
        df = pd.DataFrame({'amount': [100, 200, 300]})
        expected_types = {'amount': float, 'missing': str}
        errors = validate_data_types(df, expected_types)
        assert len(errors) == 1
        assert 'Missing required column' in errors[0]
    
    def test_validate_wrong_type(self):
        """Test validation with wrong data type."""
        df = pd.DataFrame({
            'amount': ['not_a_number', 'also_not_a_number'],
            'description': ['A', 'B']
        })
        expected_types = {'amount': float, 'description': str}
        errors = validate_data_types(df, expected_types)
        assert len(errors) == 1
        assert 'cannot be converted to float' in errors[0]


class TestSanitizeDataframe:
    """Test DataFrame sanitization."""
    
    def test_sanitize_normal_dataframe(self):
        """Test sanitization of normal DataFrame."""
        df = pd.DataFrame({
            'numeric': [100, 200, np.nan],
            'text': ['A', 'B', np.nan],
            'empty_row': [1, 2, np.nan]
        })
        result = sanitize_dataframe(df)
        
        assert result['numeric'].isna().sum() == 0  # NaN replaced with 0
        assert result['text'].isna().sum() == 0   # NaN replaced with ""
        assert len(result) == 2  # Empty row removed
    
    def test_sanitize_empty_dataframe(self):
        """Test sanitization of empty DataFrame."""
        df = pd.DataFrame()
        result = sanitize_dataframe(df)
        assert len(result) == 0
    
    def test_sanitize_all_empty_rows(self):
        """Test sanitization with all empty rows."""
        df = pd.DataFrame({
            'col1': [np.nan, np.nan, np.nan],
            'col2': [np.nan, np.nan, np.nan]
        })
        result = sanitize_dataframe(df)
        assert len(result) == 0

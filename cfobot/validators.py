"""Data validation and sanitization utilities for CFO Bot."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .constants import (
    ASSET_CLASS_CODE,
    EQUITY_CLASS_CODE,
    LIABILITY_CLASS_CODE,
    MONTH_ALIASES,
)


def sanitize_filename_component(component: str) -> str:
    """Sanitize a filename component to prevent path traversal.
    
    Args:
        component: The string to sanitize
        
    Returns:
        Sanitized string safe for use in filenames
        
    Examples:
        >>> sanitize_filename_component("MARZO")
        'MARZO'
        >>> sanitize_filename_component("../../../etc/passwd")
        'etcpasswd'
    """
    if not isinstance(component, str):
        return str(component)
    
    # Remove path traversal attempts
    sanitized = re.sub(r'[\.\/\\]', '', component)
    # Remove any remaining dangerous characters
    sanitized = re.sub(r'[<>:"|?*]', '', sanitized)
    # Limit length
    sanitized = sanitized[:50]
    
    return sanitized if sanitized else "unknown"


def validate_month_name(month: str) -> str:
    """Validate and normalize month name.
    
    Args:
        month: Month name to validate
        
    Returns:
        Normalized month name
        
    Raises:
        ValueError: If month is not recognized
        
    Examples:
        >>> validate_month_name("marzo")
        'MARZO'
        >>> validate_month_name("MAR")
        'MARZO'
    """
    if not isinstance(month, str):
        raise ValueError(f"Month must be a string, got {type(month)}")
    
    month_upper = month.upper().strip()
    
    # Direct match
    if month_upper in MONTH_ALIASES:
        return month_upper
    
    # Check aliases
    for canonical, aliases in MONTH_ALIASES.items():
        if month_upper in aliases:
            return canonical
    
    raise ValueError(f"Unknown month: {month}")


def validate_balance_equation(balance_df: pd.DataFrame) -> bool:
    """Validate that assets = liabilities + equity.
    
    Args:
        balance_df: Balance sheet DataFrame
        
    Returns:
        True if equation balances, False otherwise
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'Nivel': ['Clase', 'Clase', 'Clase'],
        ...     'Código cuenta contable': ['1', '2', '3'],
        ...     'Saldo final': [1000, 600, 400]
        ... })
        >>> validate_balance_equation(df)
        True
    """
    try:
        # Get totals by class
        assets = balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == ASSET_CLASS_CODE)
        ]["Saldo final"].sum()
        
        liabilities = abs(balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == LIABILITY_CLASS_CODE)
        ]["Saldo final"].sum())
        
        equity = abs(balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == EQUITY_CLASS_CODE)
        ]["Saldo final"].sum())
        
        # Allow for small rounding differences
        difference = abs(assets - (liabilities + equity))
        return difference < 1.0  # Less than 1 peso difference
        
    except Exception:
        return False


def detect_outliers(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Detect outliers in a financial series using z-score.
    
    Args:
        series: Pandas Series to analyze
        threshold: Z-score threshold for outlier detection
        
    Returns:
        Boolean Series indicating outliers
        
    Examples:
        >>> s = pd.Series([100, 105, 98, 1000, 102])
        >>> outliers = detect_outliers(s)
        >>> outliers.sum()
        1
    """
    if len(series) < 3:
        return pd.Series([False] * len(series), index=series.index)
    
    # Calculate z-scores
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return pd.Series([False] * len(series), index=series.index)
    
    z_scores = np.abs((series - mean) / std)
    return z_scores > threshold


def validate_account_signs(balance_df: pd.DataFrame) -> dict[str, list[str]]:
    """Validate that account balances have correct signs.
    
    Args:
        balance_df: Balance sheet DataFrame
        
    Returns:
        Dictionary with validation results and issues found
    """
    issues = {
        "negative_assets": [],
        "positive_liabilities": [],
        "negative_equity": []
    }
    
    try:
        # Check for negative assets (should be positive)
        negative_assets = balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == ASSET_CLASS_CODE) &
            (balance_df["Saldo final"] < 0)
        ]
        if not negative_assets.empty:
            issues["negative_assets"] = negative_assets["Nombre cuenta contable"].tolist()
        
        # Check for positive liabilities (should be negative)
        positive_liabilities = balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == LIABILITY_CLASS_CODE) &
            (balance_df["Saldo final"] > 0)
        ]
        if not positive_liabilities.empty:
            issues["positive_liabilities"] = positive_liabilities["Nombre cuenta contable"].tolist()
        
        # Check for negative equity (concerning)
        negative_equity = balance_df[
            (balance_df["Nivel"] == "Clase") & 
            (balance_df["Código cuenta contable"] == EQUITY_CLASS_CODE) &
            (balance_df["Saldo final"] < 0)
        ]
        if not negative_equity.empty:
            issues["negative_equity"] = negative_equity["Nombre cuenta contable"].tolist()
            
    except Exception as e:
        issues["validation_error"] = [str(e)]
    
    return issues


def validate_financial_ratios(ratios: dict[str, float]) -> dict[str, list[str]]:
    """Validate financial ratios for reasonableness.
    
    Args:
        ratios: Dictionary of calculated ratios
        
    Returns:
        Dictionary with validation warnings
    """
    warnings = {
        "liquidity_warnings": [],
        "profitability_warnings": [],
        "leverage_warnings": []
    }
    
    # Liquidity warnings
    current_ratio = ratios.get("Current Ratio", 0)
    if current_ratio < 1.0:
        warnings["liquidity_warnings"].append(
            f"Current Ratio {current_ratio:.2f} indicates potential liquidity issues"
        )
    elif current_ratio > 5.0:
        warnings["liquidity_warnings"].append(
            f"Current Ratio {current_ratio:.2f} may indicate inefficient asset utilization"
        )
    
    # Profitability warnings
    net_margin = ratios.get("Margen Neto %", 0)
    if net_margin < 0:
        warnings["profitability_warnings"].append(
            f"Negative net margin {net_margin:.2f}% indicates losses"
        )
    elif net_margin > 50:
        warnings["profitability_warnings"].append(
            f"Unusually high net margin {net_margin:.2f}% - verify calculations"
        )
    
    # Leverage warnings
    debt_equity = ratios.get("Deuda/Patrimonio", 0)
    if debt_equity > 2.0:
        warnings["leverage_warnings"].append(
            f"High debt-to-equity ratio {debt_equity:.2f} indicates high leverage"
        )
    
    return warnings


def validate_file_path(file_path: Path) -> bool:
    """Validate that file path is safe and accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if path is valid and safe
        
    Raises:
        ValueError: If path is invalid or unsafe
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    
    # Check for path traversal attempts
    if ".." in str(file_path):
        raise ValueError("Path traversal detected in file path")
    
    # Check if file exists
    if not file_path.exists():
        raise ValueError(f"File does not exist: {file_path}")
    
    # Check if it's a file (not directory)
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    # Check file extension
    if file_path.suffix.lower() not in ['.xls', '.xlsx']:
        raise ValueError(f"File must be Excel format (.xls or .xlsx), got: {file_path.suffix}")
    
    return True


def validate_data_types(df: pd.DataFrame, expected_types: dict[str, type]) -> list[str]:
    """Validate that DataFrame columns have expected data types.
    
    Args:
        df: DataFrame to validate
        expected_types: Dictionary mapping column names to expected types
        
    Returns:
        List of validation errors found
    """
    errors = []
    
    for column, expected_type in expected_types.items():
        if column not in df.columns:
            errors.append(f"Missing required column: {column}")
            continue
        
        # Check if column can be converted to expected type
        try:
            if expected_type == float:
                pd.to_numeric(df[column], errors='raise')
            elif expected_type == str:
                df[column].astype(str)
            # Add more type checks as needed
        except Exception as e:
            errors.append(f"Column '{column}' cannot be converted to {expected_type.__name__}: {e}")
    
    return errors


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize DataFrame by cleaning data and handling missing values.
    
    Args:
        df: DataFrame to sanitize
        
    Returns:
        Sanitized DataFrame
    """
    df_clean = df.copy()
    
    # Replace NaN with appropriate defaults
    numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
    df_clean[numeric_columns] = df_clean[numeric_columns].fillna(0)
    
    # Clean string columns
    string_columns = df_clean.select_dtypes(include=['object']).columns
    df_clean[string_columns] = df_clean[string_columns].fillna("").astype(str).str.strip()
    
    # Remove completely empty rows
    df_clean = df_clean.dropna(how='all')
    
    return df_clean

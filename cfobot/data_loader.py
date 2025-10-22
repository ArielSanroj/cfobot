"""Utilities for loading CFO data sources."""

from __future__ import annotations

import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

import unicodedata

import pandas as pd

from .config import AppConfig


MONTH_ALIASES: Dict[str, set[str]] = {
    "ENERO": {"ENERO", "ENE"},
    "FEBRERO": {"FEBRERO", "FEB"},
    "MARZO": {"MARZO", "MAR"},
    "ABRIL": {"ABRIL", "ABR"},
    "MAYO": {"MAYO", "MAY"},
    "JUNIO": {"JUNIO", "JUN"},
    "JULIO": {"JULIO", "JUL"},
    "AGOSTO": {"AGOSTO", "AGO"},
    "SEPTIEMBRE": {"SEPTIEMBRE", "SEP"},
    "OCTUBRE": {"OCTUBRE", "OCT"},
    "NOVIEMBRE": {"NOVIEMBRE", "NOV"},
    "DICIEMBRE": {"DICIEMBRE", "DIC"},
}

ALIAS_TO_MONTH: Dict[str, str] = {
    alias: month
    for month, aliases in MONTH_ALIASES.items()
    for alias in aliases
}


def _strip_accents(value: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", value) if unicodedata.category(c) != "Mn"
    )


def _extract_month_tokens(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    upper = _strip_accents(text.upper())
    cleaned = upper.replace("DE", " ")
    return [part for part in cleaned.split() if part.isalpha()]


def _resolve_month(label: str) -> str | None:
    for token in _extract_month_tokens(label):
        month = ALIAS_TO_MONTH.get(token)
        if month:
            return month
    return None


@dataclass
class FinancialData:
    current_month: str
    current_month_col: str
    resultado_current_col: str
    balance: pd.DataFrame
    eri: pd.DataFrame
    resultado: pd.DataFrame
    caratula: pd.DataFrame
    months: Sequence[str]
    workbook: pd.ExcelFile


def find_latest_report(config: AppConfig, logger) -> Path:
    pattern = config.paths.expand_pattern()
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No file matching '{pattern}' found")

    latest = max(files, key=lambda path: Path(path).stat().st_mtime)
    logger.info("Using report file: %s", latest)
    return Path(latest)


def _detect_month_from_filename(file_path: Path) -> str | None:
    return _resolve_month(file_path.name)


def _detect_month_from_sheet_names(
    sheet_names: Sequence[str],
    month_order: Sequence[str],
) -> str | None:
    ordered_months = {month: index for index, month in enumerate(month_order)}
    detected: List[str] = []
    for sheet_name in sheet_names:
        month = _resolve_month(sheet_name)
        if month and month in ordered_months:
            detected.append(month)

    if not detected:
        return None

    detected = sorted(set(detected), key=lambda m: ordered_months[m])
    return detected[-1]


def _detect_month_from_caratula(
    workbook: pd.ExcelFile,
    month_order: Sequence[str],
) -> str | None:
    """Detect month from CARATULA sheet content."""
    try:
        df_caratula = pd.read_excel(workbook, sheet_name="CARATULA")
        ordered_months = {month: index for index, month in enumerate(month_order)}
        
        for col in df_caratula.columns:
            for idx, val in df_caratula[col].items():
                if pd.notna(val):
                    val_str = str(val).upper()
                    for month in month_order:
                        if month in val_str:
                            return month
    except Exception:
        pass
    return None


def _previous_month(month: str, month_order: Sequence[str]) -> str:
    if month not in month_order:
        raise ValueError(f"Month '{month}' is not in configured month order")
    index = month_order.index(month)
    return month_order[index - 1] if index > 0 else month_order[-1]


def detect_current_month(
    file_path: Path,
    month_order: Sequence[str],
    workbook: pd.ExcelFile | None = None,
) -> str:
    detected_month = _detect_month_from_filename(file_path)

    if detected_month is None and workbook is not None:
        # Try sheet names first
        detected_month = _detect_month_from_sheet_names(workbook.sheet_names, month_order)
        
        # If still not found, try CARATULA sheet
        if detected_month is None:
            detected_month = _detect_month_from_caratula(workbook, month_order)

    if detected_month is None:
        raise ValueError("Could not determine report month from filename or workbook")

    # Get current month from system date
    from datetime import datetime
    current_system_month = datetime.now().strftime("%B").upper()
    
    # Map English month names to Spanish
    month_mapping = {
        'JANUARY': 'ENERO', 'FEBRUARY': 'FEBRERO', 'MARCH': 'MARZO',
        'APRIL': 'ABRIL', 'MAY': 'MAYO', 'JUNE': 'JUNIO',
        'JULY': 'JULIO', 'AUGUST': 'AGOSTO', 'SEPTEMBER': 'SEPTIEMBRE',
        'OCTOBER': 'OCTUBRE', 'NOVEMBER': 'NOVIEMBRE', 'DECEMBER': 'DICIEMBRE'
    }
    
    current_system_month_spanish = month_mapping.get(current_system_month, current_system_month)
    
    # If detected month is the current system month, analyze the previous month
    # Otherwise, analyze the detected month directly
    if detected_month == current_system_month_spanish:
        return _previous_month(detected_month, month_order)
    else:
        return detected_month


def _normalize_balance(df_balance: pd.DataFrame, current_month: str, month_order: Sequence[str]) -> pd.DataFrame:
    expected_cols = [
        "Nivel",
        "Código cuenta contable",
        "Nombre cuenta contable",
        "Saldo inicial",
        "Movimiento débito",
        "Movimiento crédito",
        "Saldo final",
    ]
    if len(df_balance.columns) >= len(expected_cols):
        extra_count = len(df_balance.columns) - len(expected_cols)
        df_balance.columns = expected_cols + [f"Extra_{i}" for i in range(extra_count)]
    else:
        df_balance.columns = [f"Col_{i}" for i in range(len(df_balance.columns))]

    df_balance["Saldo final"] = pd.to_numeric(df_balance.get("Saldo final", 0), errors="coerce").fillna(0)
    df_balance["Nivel"] = df_balance.get("Nivel", "").astype(str).fillna("")
    return df_balance


def _normalize_eri(
    df_eri: pd.DataFrame,
    current_month: str,
    month_order: Sequence[str],
) -> tuple[pd.DataFrame, List[str], str]:
    df_eri = df_eri.copy()
    df_eri.columns = [str(col).strip() for col in df_eri.columns]

    month_index = {month: index for index, month in enumerate(month_order)}
    month_columns: List[str] = []
    
    # First, try to find month names in column headers
    for column in df_eri.columns:
        column_str = str(column)
        if _resolve_month(column_str) is not None:
            month_columns.append(column_str)
    
    # If no month columns found in headers, look in the first row of data
    if not month_columns:
        for col_idx, column in enumerate(df_eri.columns):
            # Check the first few rows for month names
            for row_idx in range(min(3, len(df_eri))):
                cell_value = str(df_eri.iloc[row_idx, col_idx]).upper()
                if _resolve_month(cell_value) is not None:
                    month_columns.append(column)
                    break
    
    month_columns_sorted = sorted(
        month_columns,
        key=lambda col: month_index.get(_resolve_month(col) or col, float("inf")),
    )

    if not month_columns_sorted:
        raise ValueError("No month columns found in INFORME-ERI sheet")

    df_eri.columns = ["Codigo", "Nombre"] + list(df_eri.columns[2:-1]) + ["Observaciones"]
    df_eri["Codigo"] = df_eri["Codigo"].astype(str).fillna("")
    df_eri["Nombre"] = df_eri["Nombre"].astype(str).fillna("")
    df_eri["Display Name"] = (
        df_eri.apply(
            lambda row: row["Nombre"] if row["Nombre"].strip() else row["Codigo"],
            axis=1,
        )
    )

    for col in month_columns_sorted:
        df_eri[col] = pd.to_numeric(df_eri[col], errors="coerce").fillna(0)

    # Find the column that contains the current month data
    preferred_column = None
    for col in month_columns_sorted:
        # Check if this column contains data for the current month
        if _resolve_month(col) == current_month:
            preferred_column = col
            break
    
    # If not found by column name, look for the column with current month in the data
    if preferred_column is None:
        for col in df_eri.columns:
            for row_idx in range(min(3, len(df_eri))):
                cell_value = str(df_eri.iloc[row_idx, col]).upper()
                if current_month in cell_value:
                    preferred_column = col
                    break
            if preferred_column:
                break
    
    current_month_col = preferred_column or month_columns_sorted[-1]
    return df_eri, month_columns_sorted, current_month_col


def _normalize_resultado(
    df_resultado: pd.DataFrame,
    current_month: str,
    month_order: Sequence[str],
) -> tuple[pd.DataFrame, str]:
    df_resultado = df_resultado.copy()

    month_index = {month: index for index, month in enumerate(month_order)}

    descripcion_series = None
    normalized = None

    if isinstance(df_resultado.columns, pd.MultiIndex):
        columns = list(df_resultado.columns)
        for col in columns:
            second = str(col[1]).strip().upper()
            if "DESCRIP" in second:
                descripcion_series = df_resultado[col]
                break
        if descripcion_series is None and columns:
            descripcion_series = df_resultado[columns[0]]
        normalized = pd.DataFrame({
            "Descripcion": descripcion_series.astype(str).str.strip()
        })

        for col in columns:
            second = str(col[1]).strip().upper()
            if not second.startswith("TOTAL"):
                continue
            month_name = _resolve_month(str(col[0]))
            if not month_name:
                continue
            column_name = f"Total {month_name}"
            normalized[column_name] = pd.to_numeric(df_resultado[col], errors="coerce").fillna(0)
    else:
        df_resultado.columns = [str(col).strip() for col in df_resultado.columns]
        if "Descripcion" not in df_resultado.columns and len(df_resultado.columns) > 0:
            df_resultado = df_resultado.rename(columns={df_resultado.columns[0]: "Descripcion"})
        if "Descripcion" not in df_resultado.columns:
            df_resultado.insert(0, "Descripcion", "")
        df_resultado["Descripcion"] = df_resultado["Descripcion"].astype(str).str.strip()
        
        # Look for month columns in the data (not just headers)
        month_columns = []
        for col_idx, column in enumerate(df_resultado.columns):
            # Check the first few rows for month names
            for row_idx in range(min(3, len(df_resultado))):
                cell_value = str(df_resultado.iloc[row_idx, col_idx]).upper()
                month_name = _resolve_month(cell_value)
                if month_name and month_name in month_index:
                    month_columns.append((column, month_name))
                    break
        
        # Create normalized dataframe with month columns
        normalized = df_resultado[["Descripcion"]].copy()
        
        for col, month_name in month_columns:
            column_name = f"Total {month_name}"
            # Get the data from the column, skipping the header rows (first 2 rows)
            data = df_resultado[col].iloc[2:].reset_index(drop=True)
            normalized[column_name] = pd.to_numeric(data, errors="coerce").fillna(0)

    total_columns = [col for col in normalized.columns if col.startswith("Total ")]

    if not total_columns:
        raise ValueError("No total columns detected in ESTADO RESULTADO sheet")

    preferred_column = f"Total {current_month}"
    if preferred_column in normalized.columns:
        current_total_column = preferred_column
    else:
        sorted_columns = sorted(
            total_columns,
            key=lambda col: month_index.get(col.replace("Total ", ""), float("inf")),
        )
        current_total_column = sorted_columns[-1]

    for col in normalized.columns:
        if col == "Descripcion" or not col.startswith("Total "):
            continue
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)

    return normalized, current_total_column


def load_financial_data(file_path: Path, config: AppConfig, logger) -> FinancialData:
    """Load and validate financial data from Excel file.
    
    Args:
        file_path: Path to the Excel file
        config: Application configuration
        logger: Logger instance
        
    Returns:
        FinancialData object with loaded and normalized data
        
    Raises:
        ValueError: If required sheets are missing or data is invalid
        FileNotFoundError: If file doesn't exist
    """
    workbook = pd.ExcelFile(file_path)
    logger.debug("Available sheets: %s", workbook.sheet_names)

    current_month = detect_current_month(
        file_path,
        config.month_order,
        workbook=workbook,
    )

    # Validate all required sheets exist before processing
    required_sheets = ["INFORME-ERI", "ESTADO RESULTADO", "CARATULA"]
    
    # Find the correct balance sheet name that matches the current month
    balance_sheet = None
    for sheet_name in workbook.sheet_names:
        if sheet_name.startswith("BALANCE ") and _resolve_month(sheet_name) == current_month:
            balance_sheet = sheet_name
            break
    
    if balance_sheet is None:
        available_sheets = ", ".join(workbook.sheet_names)
        raise ValueError(
            f"Could not find balance sheet for month '{current_month}'. "
            f"Available sheets: {available_sheets}"
        )
    
    required_sheets.append(balance_sheet)
    
    missing_sheets = [sheet for sheet in required_sheets if sheet not in workbook.sheet_names]
    if missing_sheets:
        available_sheets = ", ".join(workbook.sheet_names)
        raise ValueError(
            f"Required sheets missing: {', '.join(missing_sheets)}. "
            f"Available sheets: {available_sheets}"
        )

    try:
        df_balance = pd.read_excel(workbook, sheet_name=balance_sheet, skiprows=4)
        df_eri = pd.read_excel(workbook, sheet_name="INFORME-ERI", skiprows=1)
        df_resultado = pd.read_excel(
            workbook,
            sheet_name="ESTADO RESULTADO",
            skiprows=2,
            header=[0, 1],
        )
        df_caratula = pd.read_excel(workbook, sheet_name="CARATULA", skiprows=5)
    except Exception as e:
        raise ValueError(f"Failed to read Excel sheets: {e}")

    df_balance = _normalize_balance(df_balance, current_month, config.month_order)
    df_eri, months, current_month_col = _normalize_eri(df_eri, current_month, config.month_order)
    df_resultado, current_resultado_col = _normalize_resultado(
        df_resultado,
        current_month=current_month,
        month_order=config.month_order,
    )

    return FinancialData(
        current_month=current_month,
        current_month_col=current_month_col,
        resultado_current_col=current_resultado_col,
        balance=df_balance,
        eri=df_eri,
        resultado=df_resultado,
        caratula=df_caratula,
        months=months,
        workbook=workbook,
    )

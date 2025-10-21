"""Utilities for loading CFO data sources."""

from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

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


def detect_current_month(file_path: Path, month_order: Sequence[str]) -> str:
    match = re.search(r"DE (\w+) APRU", file_path.name)
    if not match:
        raise ValueError("Could not extract month from filename")

    month = match.group(1).upper()
    if month not in month_order:
        raise ValueError(f"Month '{month}' is not in configured month order")
    return month


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
    for column in df_eri.columns:
        column_str = str(column)
        if _resolve_month(column_str) is not None:
            month_columns.append(column_str)
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

    preferred_column = next(
        (col for col in month_columns_sorted if _resolve_month(col) == current_month),
        None,
    )
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
        normalized = df_resultado.copy()

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
    workbook = pd.ExcelFile(file_path)
    logger.debug("Available sheets: %s", workbook.sheet_names)

    current_month = detect_current_month(file_path, config.month_order)
    balance_sheet = f"BALANCE {current_month}"
    if balance_sheet not in workbook.sheet_names:
        raise ValueError(f"Sheet '{balance_sheet}' not found in workbook")

    df_balance = pd.read_excel(workbook, sheet_name=balance_sheet, skiprows=4)
    df_eri = pd.read_excel(workbook, sheet_name="INFORME-ERI", skiprows=1)
    df_resultado = pd.read_excel(
        workbook,
        sheet_name="ESTADO RESULTADO",
        skiprows=2,
        header=[0, 1],
    )
    df_caratula = pd.read_excel(workbook, sheet_name="CARATULA", skiprows=5)

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

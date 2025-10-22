from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cfobot.config import DEFAULT_MONTH_ORDER
from cfobot.data_loader import detect_current_month


def test_detect_current_month_success(tmp_path: Path):
    file_path = tmp_path / "INFORME DE MARZO APRU- 2025 .xls"
    file_path.touch()
    workbook = SimpleNamespace(sheet_names=["BALANCE FEBRERO", "BALANCE MARZO"])

    month = detect_current_month(file_path, DEFAULT_MONTH_ORDER, workbook=workbook)

    assert month == "FEBRERO"


def test_detect_current_month_fallback_to_workbook(tmp_path: Path):
    file_path = tmp_path / "reporte_sin_mes.xls"
    file_path.touch()
    workbook = SimpleNamespace(sheet_names=["BALANCE SEPTIEMBRE", "BALANCE OCTUBRE"])

    month = detect_current_month(file_path, DEFAULT_MONTH_ORDER, workbook=workbook)

    assert month == "SEPTIEMBRE"


def test_detect_current_month_invalid(tmp_path: Path):
    file_path = tmp_path / "reporte_sin_mes.xls"
    file_path.touch()
    workbook = SimpleNamespace(sheet_names=["INFORME-ERI", "CARATULA"])

    with pytest.raises(ValueError):
        detect_current_month(file_path, DEFAULT_MONTH_ORDER, workbook=workbook)

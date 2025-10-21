import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cfobot.config import AppConfig, load_config


def test_load_config_defaults():
    config = load_config()
    assert isinstance(config, AppConfig)
    assert config.paths.downloads_dir.exists()
    assert config.budgets.ingresos_mensual > 0

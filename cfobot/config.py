"""Application configuration handling."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

DEFAULT_MONTH_ORDER: List[str] = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]


@dataclass
class PathConfig:
    downloads_dir: Path = Path.home() / "Downloads"
    report_pattern: str = "INFORME DE * APRU- 2025 .xls"

    def expand_pattern(self) -> str:
        return str(self.downloads_dir / self.report_pattern)


@dataclass
class BudgetConfig:
    ingresos_mensual: float = 100_000_000
    gastos_mensual: float = 125_000_000


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    recipient_emails: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "EmailConfig | None":
        sender = os.getenv("CFOBOT_EMAIL_SENDER")
        password = os.getenv("CFOBOT_EMAIL_PASSWORD")
        recipient = os.getenv("CFOBOT_EMAIL_RECIPIENT")

        if not sender or not password or not recipient:
            return None

        recipients: list[str] = [
            email.strip() for email in recipient.split(",") if email.strip()
        ]

        return cls(
            smtp_server=os.getenv("CFOBOT_EMAIL_SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("CFOBOT_EMAIL_SMTP_PORT", "587")),
            sender_email=sender,
            sender_password=password,
            recipient_emails=list(recipients),
        )


@dataclass
class AppConfig:
    paths: PathConfig = PathConfig()
    budgets: BudgetConfig = BudgetConfig()
    month_order: List[str] = field(default_factory=lambda: DEFAULT_MONTH_ORDER.copy())
    email: EmailConfig | None = field(default=None)
    generate_visuals: bool = True


def load_config() -> AppConfig:
    """Load configuration from environment."""

    email_config = EmailConfig.from_env()

    config = AppConfig(email=email_config)
    return config

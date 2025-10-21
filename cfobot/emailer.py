"""Email sending helpers."""

from __future__ import annotations

import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import Iterable

from .config import EmailConfig


def send_reports(
    email_config: EmailConfig,
    subject: str,
    html_body: str,
    attachments: Iterable[Path],
) -> None:
    message = MIMEMultipart()
    message["From"] = email_config.sender_email
    message["To"] = ", ".join(email_config.recipient_emails)
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    for attachment in attachments:
        path = Path(attachment).expanduser()
        if not path.exists():
            continue
        with path.open("rb") as file_handle:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file_handle.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={path.name}")
            message.attach(part)

    with smtplib.SMTP(email_config.smtp_server, email_config.smtp_port) as server:
        server.starttls()
        server.login(email_config.sender_email, email_config.sender_password)
        server.send_message(message)

"""Email sending helpers."""

from __future__ import annotations

import logging
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import Iterable

from .config import EmailConfig

logger = logging.getLogger(__name__)


def send_reports(
    email_config: EmailConfig,
    subject: str,
    html_body: str,
    attachments: Iterable[Path],
) -> None:
    """Send email with attachments and comprehensive error handling.
    
    Args:
        email_config: Email configuration with SMTP settings
        subject: Email subject line
        html_body: HTML content of the email
        attachments: Iterable of file paths to attach
        
    Raises:
        ValueError: If email configuration is invalid
        ConnectionError: If SMTP connection fails
        smtplib.SMTPException: If email sending fails
    """
    try:
        # Validate email configuration
        if not email_config.sender_email or not email_config.sender_password:
            raise ValueError("Email sender credentials are missing")
        
        if not email_config.recipient_emails:
            raise ValueError("No recipient emails configured")
        
        logger.info(f"Preparing email to {len(email_config.recipient_emails)} recipients")
        
        # Create message
        message = MIMEMultipart()
        message["From"] = email_config.sender_email
        message["To"] = ", ".join(email_config.recipient_emails)
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        # Add attachments
        attachment_count = 0
        for attachment in attachments:
            path = Path(attachment).expanduser()
            if not path.exists():
                logger.warning(f"Attachment not found: {path}")
                continue
            try:
                with path.open("rb") as file_handle:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file_handle.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={path.name}")
                    message.attach(part)
                    attachment_count += 1
                    logger.debug(f"Added attachment: {path.name}")
            except Exception as e:
                logger.error(f"Failed to attach {path}: {e}")
                continue
        
        logger.info(f"Email prepared with {attachment_count} attachments")

        # Send email with timeout and retry logic
        try:
            with smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30) as server:
                logger.info(f"Connecting to SMTP server: {email_config.smtp_server}:{email_config.smtp_port}")
                server.starttls()
                server.login(email_config.sender_email, email_config.sender_password)
                server.send_message(message)
                logger.info("Email sent successfully")
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise ConnectionError(f"Failed to authenticate with SMTP server: {e}")
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed: {e}")
            raise ConnectionError(f"Failed to connect to SMTP server: {e}")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise ConnectionError(f"Failed to send email: {e}")
            
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise

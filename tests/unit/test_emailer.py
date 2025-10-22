"""Unit tests for emailer module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cfobot.emailer import send_reports
from cfobot.config import EmailConfig


@pytest.fixture
def sample_email_config():
    """Create sample email configuration for testing."""
    return EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="test@example.com",
        sender_password="test_password",
        recipient_emails=["recipient1@example.com", "recipient2@example.com"]
    )


@pytest.fixture
def sample_attachments(tmp_path):
    """Create sample attachment files for testing."""
    file1 = tmp_path / "report1.xlsx"
    file2 = tmp_path / "report2.png"
    file1.write_text("test content 1")
    file2.write_text("test content 2")
    return [file1, file2]


class TestSendReports:
    """Test email sending functionality."""
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_success(self, mock_smtp, sample_email_config, sample_attachments):
        """Test successful email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        send_reports(
            email_config=sample_email_config,
            subject="Test Subject",
            html_body="<html>Test Body</html>",
            attachments=sample_attachments
        )
        
        # Verify SMTP connection
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587, timeout=30)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.send_message.assert_called_once()
    
    def test_send_reports_missing_sender_email(self, sample_email_config, sample_attachments):
        """Test email sending with missing sender email."""
        sample_email_config.sender_email = ""
        
        with pytest.raises(ValueError, match="Email sender credentials are missing"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    def test_send_reports_missing_sender_password(self, sample_email_config, sample_attachments):
        """Test email sending with missing sender password."""
        sample_email_config.sender_password = ""
        
        with pytest.raises(ValueError, match="Email sender credentials are missing"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    def test_send_reports_no_recipients(self, sample_email_config, sample_attachments):
        """Test email sending with no recipients."""
        sample_email_config.recipient_emails = []
        
        with pytest.raises(ValueError, match="No recipient emails configured"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_missing_attachment(self, mock_smtp, sample_email_config, tmp_path):
        """Test email sending with missing attachment file."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        missing_file = tmp_path / "missing_file.xlsx"
        attachments = [missing_file]
        
        send_reports(
            email_config=sample_email_config,
            subject="Test Subject",
            html_body="<html>Test Body</html>",
            attachments=attachments
        )
        
        # Should still send email without the missing attachment
        mock_server.send_message.assert_called_once()
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_attachment_error(self, mock_smtp, sample_email_config, tmp_path):
        """Test email sending with attachment file error."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Create a file that will cause an error when reading
        problematic_file = tmp_path / "problematic.xlsx"
        problematic_file.write_text("test")
        
        # Mock the file open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=[problematic_file]
            )
        
        # Should still send email without the problematic attachment
        mock_server.send_message.assert_called_once()
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_smtp_authentication_error(self, mock_smtp, sample_email_config, sample_attachments):
        """Test email sending with SMTP authentication error."""
        from smtplib import SMTPAuthenticationError
        
        mock_smtp.side_effect = SMTPAuthenticationError(535, "Authentication failed")
        
        with pytest.raises(ConnectionError, match="Failed to authenticate with SMTP server"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_smtp_connection_error(self, mock_smtp, sample_email_config, sample_attachments):
        """Test email sending with SMTP connection error."""
        from smtplib import SMTPConnectError
        
        mock_smtp.side_effect = SMTPConnectError(421, "Connection failed")
        
        with pytest.raises(ConnectionError, match="Failed to connect to SMTP server"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_smtp_general_error(self, mock_smtp, sample_email_config, sample_attachments):
        """Test email sending with general SMTP error."""
        from smtplib import SMTPException
        
        mock_smtp.side_effect = SMTPException("General SMTP error")
        
        with pytest.raises(SMTPException):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_unexpected_error(self, mock_smtp, sample_email_config, sample_attachments):
        """Test email sending with unexpected error."""
        mock_smtp.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ConnectionError, match="Failed to send email"):
            send_reports(
                email_config=sample_email_config,
                subject="Test Subject",
                html_body="<html>Test Body</html>",
                attachments=sample_attachments
            )
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_no_attachments(self, mock_smtp, sample_email_config):
        """Test email sending with no attachments."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        send_reports(
            email_config=sample_email_config,
            subject="Test Subject",
            html_body="<html>Test Body</html>",
            attachments=[]
        )
        
        # Should still send email without attachments
        mock_server.send_message.assert_called_once()
    
    @patch('cfobot.emailer.smtplib.SMTP')
    def test_send_reports_verify_message_content(self, mock_smtp, sample_email_config, sample_attachments):
        """Test that email message content is correct."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        send_reports(
            email_config=sample_email_config,
            subject="Test Subject",
            html_body="<html>Test Body</html>",
            attachments=sample_attachments
        )
        
        # Get the message that was sent
        sent_message = mock_server.send_message.call_args[0][0]
        
        # Verify message headers
        assert sent_message["From"] == "test@example.com"
        assert sent_message["To"] == "recipient1@example.com, recipient2@example.com"
        assert sent_message["Subject"] == "Test Subject"
        
        # Verify message has HTML body
        assert len(sent_message.get_payload()) >= 1  # At least HTML body
        assert any(part.get_content_type() == "text/html" for part in sent_message.get_payload())
        
        # Verify attachments
        attachment_parts = [part for part in sent_message.get_payload() 
                           if part.get_content_type() == "application/octet-stream"]
        assert len(attachment_parts) == 2  # Two attachments

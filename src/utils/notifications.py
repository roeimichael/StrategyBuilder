"""
Notification utilities for StrategyBuilder
Supports Telegram and Email notifications
"""
import os
from typing import Optional
import smtplib
from email.message import EmailMessage


class TelegramNotifier:
    """Send notifications via Telegram"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None

        if self.bot_token:
            try:
                import telebot
                self.bot = telebot.TeleBot(self.bot_token)
            except ImportError:
                print("Warning: pyTelegramBotAPI not installed. Install with: pip install pyTelegramBotAPI")

    def send_message(self, message: str) -> bool:
        """Send a message via Telegram"""
        if not self.bot or not self.chat_id:
            print("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
            return False

        try:
            self.bot.send_message(self.chat_id, message)
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False


class EmailNotifier:
    """Send notifications via Email"""

    def __init__(self):
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))

    def send_email(self, subject: str, body: str, to: Optional[str] = None) -> bool:
        """Send an email notification"""
        if not self.email_address or not self.email_password:
            print("Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.")
            return False

        to = to or self.email_address  # Send to self if no recipient specified

        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['subject'] = subject
            msg['to'] = to
            msg['from'] = self.email_address

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


def send_notification(message: str, method: str = 'both') -> bool:
    """
    Send notification via specified method

    Args:
        message: The message to send
        method: 'telegram', 'email', or 'both'

    Returns:
        True if at least one notification succeeded
    """
    success = False

    if method in ['telegram', 'both']:
        telegram = TelegramNotifier()
        success = telegram.send_message(message) or success

    if method in ['email', 'both']:
        email = EmailNotifier()
        success = email.send_email('StrategyBuilder Notification', message) or success

    return success

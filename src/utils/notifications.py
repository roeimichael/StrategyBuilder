"""Real-time notification system for trading alerts

This module provides email notification capabilities for:
- Trading signal alerts
- Backtest completion notifications
- Performance threshold alerts
- System status updates
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmailNotifier:
    """Email notification system for trading alerts"""

    def __init__(self, smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize email notifier

        Args:
            smtp_server: SMTP server address (default: from environment)
            smtp_port: SMTP port (default: from environment)
            username: Email username (default: from environment)
            password: Email password (default: from environment)
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')

        if not self.username or not self.password:
            raise ValueError(
                "Email credentials not configured. Set EMAIL_USERNAME and EMAIL_PASSWORD "
                "environment variables or pass them to the constructor."
            )

    def send_email(self, to_email: str, subject: str, body: str,
                  html_body: Optional[str] = None,
                  attachments: Optional[List[str]] = None) -> bool:
        """
        Send email notification

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            attachments: Optional list of file paths to attach

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))

            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Add attachments if provided
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(filepath)}'
                            )
                            msg.attach(part)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_trading_signal_alert(self, to_email: str, signal_data: Dict[str, Any]) -> bool:
        """
        Send trading signal alert

        Args:
            to_email: Recipient email address
            signal_data: Trading signal data dictionary

        Returns:
            True if email sent successfully
        """
        ticker = signal_data.get('ticker', 'Unknown')
        signal_type = signal_data.get('type', 'Signal')  # BUY or SELL
        price = signal_data.get('price', 0)
        timestamp = signal_data.get('timestamp', datetime.now())
        strategy = signal_data.get('strategy', 'Unknown Strategy')
        confidence = signal_data.get('confidence', 'N/A')

        subject = f"🔔 Trading Signal: {signal_type} {ticker}"

        body = f"""
Trading Signal Alert
====================

Ticker: {ticker}
Signal: {signal_type}
Price: ${price:.2f}
Strategy: {strategy}
Confidence: {confidence}
Time: {timestamp}

This is an automated trading signal from StrategyBuilder Pro.
Please review the signal before taking any action.

---
StrategyBuilder Pro
Automated Trading System
"""

        html_body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            background-color: {'#4CAF50' if signal_type == 'BUY' else '#F44336'};
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .signal-details {{
            background-color: white;
            padding: 15px;
            border-left: 4px solid {'#4CAF50' if signal_type == 'BUY' else '#F44336'};
            margin: 20px 0;
        }}
        .detail-row {{
            margin: 10px 0;
        }}
        .label {{
            font-weight: bold;
            color: #666;
        }}
        .value {{
            color: #333;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔔 Trading Signal Alert</h1>
        <h2>{signal_type} {ticker}</h2>
    </div>

    <div class="content">
        <div class="signal-details">
            <div class="detail-row">
                <span class="label">Ticker:</span>
                <span class="value">{ticker}</span>
            </div>
            <div class="detail-row">
                <span class="label">Signal:</span>
                <span class="value" style="font-weight: bold; font-size: 18px; color: {'#4CAF50' if signal_type == 'BUY' else '#F44336'};">
                    {signal_type}
                </span>
            </div>
            <div class="detail-row">
                <span class="label">Price:</span>
                <span class="value">${price:.2f}</span>
            </div>
            <div class="detail-row">
                <span class="label">Strategy:</span>
                <span class="value">{strategy}</span>
            </div>
            <div class="detail-row">
                <span class="label">Confidence:</span>
                <span class="value">{confidence}</span>
            </div>
            <div class="detail-row">
                <span class="label">Time:</span>
                <span class="value">{timestamp}</span>
            </div>
        </div>

        <p style="color: #666; font-style: italic;">
            This is an automated trading signal from StrategyBuilder Pro.
            Please review the signal before taking any action.
        </p>
    </div>

    <div class="footer">
        <p>StrategyBuilder Pro - Automated Trading System</p>
        <p>© {datetime.now().year} All rights reserved</p>
    </div>
</body>
</html>
"""

        return self.send_email(to_email, subject, body, html_body)

    def send_backtest_completion_alert(self, to_email: str,
                                      results: Dict[str, Any],
                                      report_path: Optional[str] = None) -> bool:
        """
        Send backtest completion notification

        Args:
            to_email: Recipient email address
            results: Backtest results dictionary
            report_path: Optional path to PDF/HTML report to attach

        Returns:
            True if email sent successfully
        """
        ticker = results.get('ticker', 'Unknown')
        return_pct = results.get('return_pct', 0)
        total_trades = results.get('total_trades', 0)
        sharpe_ratio = results.get('sharpe_ratio', 0)

        subject = f"📊 Backtest Complete: {ticker} ({return_pct:+.2f}%)"

        body = f"""
Backtest Completion Alert
=========================

Ticker: {ticker}
Total Return: {return_pct:.2f}%
Total Trades: {total_trades}
Sharpe Ratio: {sharpe_ratio:.3f}
Max Drawdown: {results.get('max_drawdown', 0):.2f}%

Start Date: {results.get('start_date', 'N/A')}
End Date: {results.get('end_date', 'N/A')}

{'Report attached.' if report_path else 'No report attached.'}

---
StrategyBuilder Pro
"""

        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #1976D2; color: white; padding: 20px; text-align: center; }}
        .metrics {{ padding: 20px; }}
        .metric {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        .value {{ color: #333; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #F44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Backtest Complete</h1>
        <h2>{ticker}</h2>
    </div>

    <div class="metrics">
        <div class="metric">
            <span class="label">Total Return:</span>
            <span class="value {'positive' if return_pct > 0 else 'negative'}" style="font-size: 18px; font-weight: bold;">
                {return_pct:+.2f}%
            </span>
        </div>
        <div class="metric">
            <span class="label">Total Trades:</span>
            <span class="value">{total_trades}</span>
        </div>
        <div class="metric">
            <span class="label">Sharpe Ratio:</span>
            <span class="value">{sharpe_ratio:.3f}</span>
        </div>
        <div class="metric">
            <span class="label">Max Drawdown:</span>
            <span class="value negative">{results.get('max_drawdown', 0):.2f}%</span>
        </div>
    </div>

    <div style="text-align: center; padding: 20px; color: #666;">
        <p>StrategyBuilder Pro - Professional Backtesting Platform</p>
    </div>
</body>
</html>
"""

        attachments = [report_path] if report_path and os.path.exists(report_path) else None

        return self.send_email(to_email, subject, body, html_body, attachments)

    def send_performance_threshold_alert(self, to_email: str,
                                        alert_type: str,
                                        current_value: float,
                                        threshold: float,
                                        ticker: str = "Portfolio") -> bool:
        """
        Send performance threshold alert

        Args:
            to_email: Recipient email address
            alert_type: Type of alert (e.g., "Drawdown", "Return", "Loss")
            current_value: Current metric value
            threshold: Threshold that was crossed
            ticker: Ticker or portfolio name

        Returns:
            True if email sent successfully
        """
        subject = f"⚠️ Alert: {alert_type} Threshold Reached - {ticker}"

        body = f"""
Performance Threshold Alert
===========================

Alert Type: {alert_type}
Ticker/Portfolio: {ticker}
Current Value: {current_value:.2f}
Threshold: {threshold:.2f}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review your positions and consider taking appropriate action.

---
StrategyBuilder Pro
"""

        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
        .alert-details {{ padding: 20px; background-color: #FFF3E0; border-left: 4px solid #FF9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ Performance Threshold Alert</h1>
    </div>

    <div class="alert-details">
        <h2>{alert_type} Threshold Reached</h2>
        <p><strong>Ticker/Portfolio:</strong> {ticker}</p>
        <p><strong>Current Value:</strong> {current_value:.2f}</p>
        <p><strong>Threshold:</strong> {threshold:.2f}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <p style="margin-top: 20px; color: #666;">
            Please review your positions and consider taking appropriate action.
        </p>
    </div>

    <div style="text-align: center; padding: 20px; color: #666;">
        <p>StrategyBuilder Pro - Automated Alert System</p>
    </div>
</body>
</html>
"""

        return self.send_email(to_email, subject, body, html_body)


def create_env_template(filename: str = ".env.example"):
    """
    Create .env template file with email configuration

    Args:
        filename: Output filename
    """
    template = """# Email Notification Configuration
# Copy this file to .env and fill in your credentials

# SMTP Server Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Email Credentials
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Notification Recipients (comma-separated)
ALERT_RECIPIENTS=trader@example.com

# Enable/Disable Notifications
ENABLE_EMAIL_NOTIFICATIONS=false

# Alert Thresholds
MAX_DRAWDOWN_THRESHOLD=10.0  # %
MIN_RETURN_THRESHOLD=-5.0    # %
"""

    with open(filename, 'w') as f:
        f.write(template)

    print(f"Created {filename}. Copy to .env and configure your credentials.")


# Example usage
if __name__ == "__main__":
    # Create .env template
    create_env_template()

    # Example: Send trading signal alert
    # notifier = EmailNotifier()
    # signal = {
    #     'ticker': 'AAPL',
    #     'type': 'BUY',
    #     'price': 150.25,
    #     'strategy': 'Bollinger Bands',
    #     'confidence': 'High',
    #     'timestamp': datetime.now()
    # }
    # notifier.send_trading_signal_alert('trader@example.com', signal)

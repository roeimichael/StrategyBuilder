"""Professional reporting with PDF and HTML export

This module generates comprehensive performance reports including:
- Performance summary tables
- Charts and visualizations
- Trade analysis
- Risk metrics
- PDF and HTML export
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import io

# Optional PDF generation dependencies
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                    Spacer, PageBreak, Image)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from PIL import Image as PILImage
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Create dummy classes/values for when reportlab is not available
    colors = None
    letter = None
    A4 = None
    inch = 1


class ProfessionalReportGenerator:
    """Generate professional backtesting reports"""

    def __init__(self, results: Dict[str, Any], output_dir: str = "data/reports"):
        """
        Initialize report generator

        Args:
            results: Backtest results dictionary
            output_dir: Directory to save reports
        """
        self.results = results
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._create_custom_styles()
        else:
            self.styles = None

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        if not REPORTLAB_AVAILABLE:
            return

        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceBefore=20,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#616161')
        ))

    def generate_pdf_report(self, filename: Optional[str] = None) -> str:
        """
        Generate PDF report

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated PDF file

        Raises:
            ImportError: If reportlab is not installed
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        if filename is None:
            ticker = self.results.get('ticker', 'strategy')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ticker}_backtest_report_{timestamp}.pdf"

        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Title
        title = Paragraph(
            f"Backtest Report: {self.results.get('ticker', 'Strategy')}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Report metadata
        metadata = [
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"<b>Start Date:</b> {self.results.get('start_date', 'N/A')}",
            f"<b>End Date:</b> {self.results.get('end_date', 'N/A')}",
            f"<b>Interval:</b> {self.results.get('interval', '1d')}"
        ]

        for item in metadata:
            story.append(Paragraph(item, self.styles['Normal']))

        story.append(Spacer(1, 20))

        # Performance Summary
        story.append(Paragraph("Performance Summary", self.styles['SectionHeader']))
        performance_table = self._create_performance_table()
        story.append(performance_table)
        story.append(Spacer(1, 20))

        # Risk Metrics
        story.append(Paragraph("Risk Metrics", self.styles['SectionHeader']))
        risk_table = self._create_risk_metrics_table()
        story.append(risk_table)
        story.append(Spacer(1, 20))

        # Trade Statistics
        if self.results.get('total_trades', 0) > 0:
            story.append(Paragraph("Trade Statistics", self.styles['SectionHeader']))
            trade_table = self._create_trade_statistics_table()
            story.append(trade_table)
            story.append(Spacer(1, 20))

        # Advanced Metrics
        if 'advanced_metrics' in self.results:
            story.append(PageBreak())
            story.append(Paragraph("Advanced Metrics", self.styles['SectionHeader']))
            advanced_table = self._create_advanced_metrics_table()
            story.append(advanced_table)

        # Build PDF
        doc.build(story)

        return filepath

    def _create_performance_table(self) -> 'Table':
        """Create performance summary table"""
        data = [
            ['Metric', 'Value'],
            ['Initial Capital', f"${self.results.get('start_value', 0):,.2f}"],
            ['Final Value', f"${self.results.get('end_value', 0):,.2f}"],
            ['Total Return', f"{self.results.get('return_pct', 0):.2f}%"],
            ['Total P&L', f"${self.results.get('pnl', 0):,.2f}"],
            ['Total Trades', str(self.results.get('total_trades', 0))]
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_risk_metrics_table(self) -> 'Table':
        """Create risk metrics table"""
        data = [
            ['Metric', 'Value'],
            ['Sharpe Ratio', f"{self.results.get('sharpe_ratio', 0):.3f}"],
            ['Max Drawdown', f"{self.results.get('max_drawdown', 0):.2f}%"],
        ]

        # Add Sortino and Calmar if available
        advanced = self.results.get('advanced_metrics', {})
        if advanced:
            sortino = advanced.get('sortino_ratio')
            if sortino is not None:
                data.append(['Sortino Ratio', f"{sortino:.3f}"])

            calmar = advanced.get('calmar_ratio')
            if calmar is not None:
                data.append(['Calmar Ratio', f"{calmar:.3f}"])

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_trade_statistics_table(self) -> 'Table':
        """Create trade statistics table"""
        advanced = self.results.get('advanced_metrics', {})

        data = [
            ['Metric', 'Value'],
            ['Total Trades', str(self.results.get('total_trades', 0))],
            ['Win Rate', f"{advanced.get('win_rate', 0):.2f}%"],
            ['Profit Factor', f"{advanced.get('profit_factor', 0):.2f}" if advanced.get('profit_factor') else 'N/A'],
            ['Payoff Ratio', f"{advanced.get('payoff_ratio', 0):.2f}" if advanced.get('payoff_ratio') else 'N/A'],
            ['Avg Win', f"${advanced.get('avg_win', 0):.2f}"],
            ['Avg Loss', f"${advanced.get('avg_loss', 0):.2f}"],
            ['Max Consecutive Wins', str(advanced.get('max_consecutive_wins', 0))],
            ['Max Consecutive Losses', str(advanced.get('max_consecutive_losses', 0))],
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def _create_advanced_metrics_table(self) -> 'Table':
        """Create advanced metrics table"""
        advanced = self.results.get('advanced_metrics', {})

        data = [
            ['Metric', 'Value'],
            ['Expectancy', f"${advanced.get('expectancy', 0):.2f}"],
            ['Largest Win', f"${advanced.get('largest_win', 0):.2f}"],
            ['Largest Loss', f"${advanced.get('largest_loss', 0):.2f}"],
        ]

        # Add recovery periods if available
        recovery_periods = advanced.get('recovery_periods', [])
        if recovery_periods:
            avg_recovery = sum(r['recovery_days'] for r in recovery_periods) / len(recovery_periods)
            data.append(['Avg Recovery Period', f"{avg_recovery:.1f} days"])

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return table

    def generate_html_report(self, filename: Optional[str] = None) -> str:
        """
        Generate HTML report

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated HTML file
        """
        if filename is None:
            ticker = self.results.get('ticker', 'strategy')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ticker}_backtest_report_{timestamp}.html"

        filepath = os.path.join(self.output_dir, filename)

        html_content = self._generate_html_content()

        with open(filepath, 'w') as f:
            f.write(html_content)

        return filepath

    def _generate_html_content(self) -> str:
        """Generate HTML content"""
        ticker = self.results.get('ticker', 'Strategy')
        advanced = self.results.get('advanced_metrics', {})

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtest Report - {ticker}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #1976D2;
            border-bottom: 3px solid #1976D2;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #424242;
            margin-top: 30px;
        }}
        .metadata {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .metadata p {{
            margin: 5px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #1976D2;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .metric-value {{
            font-weight: bold;
            color: #1976D2;
        }}
        .positive {{
            color: #4CAF50;
        }}
        .negative {{
            color: #F44336;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Backtest Report: {ticker}</h1>

        <div class="metadata">
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Start Date:</strong> {self.results.get('start_date', 'N/A')}</p>
            <p><strong>End Date:</strong> {self.results.get('end_date', 'N/A')}</p>
            <p><strong>Interval:</strong> {self.results.get('interval', '1d')}</p>
        </div>

        <h2>Performance Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Initial Capital</td>
                <td class="metric-value">${self.results.get('start_value', 0):,.2f}</td>
            </tr>
            <tr>
                <td>Final Value</td>
                <td class="metric-value">${self.results.get('end_value', 0):,.2f}</td>
            </tr>
            <tr>
                <td>Total Return</td>
                <td class="metric-value {'positive' if self.results.get('return_pct', 0) > 0 else 'negative'}">
                    {self.results.get('return_pct', 0):.2f}%
                </td>
            </tr>
            <tr>
                <td>Total P&L</td>
                <td class="metric-value {'positive' if self.results.get('pnl', 0) > 0 else 'negative'}">
                    ${self.results.get('pnl', 0):,.2f}
                </td>
            </tr>
            <tr>
                <td>Total Trades</td>
                <td class="metric-value">{self.results.get('total_trades', 0)}</td>
            </tr>
        </table>

        <h2>Risk Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Sharpe Ratio</td>
                <td class="metric-value">{self.results.get('sharpe_ratio', 0):.3f}</td>
            </tr>
            <tr>
                <td>Max Drawdown</td>
                <td class="metric-value negative">{self.results.get('max_drawdown', 0):.2f}%</td>
            </tr>
            {'<tr><td>Sortino Ratio</td><td class="metric-value">' + f"{advanced.get('sortino_ratio', 0):.3f}" + '</td></tr>' if advanced.get('sortino_ratio') else ''}
            {'<tr><td>Calmar Ratio</td><td class="metric-value">' + f"{advanced.get('calmar_ratio', 0):.3f}" + '</td></tr>' if advanced.get('calmar_ratio') else ''}
        </table>

        <h2>Trade Statistics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Win Rate</td>
                <td class="metric-value">{advanced.get('win_rate', 0):.2f}%</td>
            </tr>
            <tr>
                <td>Profit Factor</td>
                <td class="metric-value">{f"{advanced.get('profit_factor', 0):.2f}" if advanced.get('profit_factor') else 'N/A'}</td>
            </tr>
            <tr>
                <td>Payoff Ratio</td>
                <td class="metric-value">{f"{advanced.get('payoff_ratio', 0):.2f}" if advanced.get('payoff_ratio') else 'N/A'}</td>
            </tr>
            <tr>
                <td>Average Win</td>
                <td class="metric-value positive">${advanced.get('avg_win', 0):.2f}</td>
            </tr>
            <tr>
                <td>Average Loss</td>
                <td class="metric-value negative">${advanced.get('avg_loss', 0):.2f}</td>
            </tr>
            <tr>
                <td>Expectancy</td>
                <td class="metric-value">${advanced.get('expectancy', 0):.2f}</td>
            </tr>
        </table>

        <div class="footer">
            <p>Generated by StrategyBuilder Pro</p>
            <p>© {datetime.now().year} - Professional Backtesting Platform</p>
        </div>
    </div>
</body>
</html>
"""
        return html


def export_trade_history_csv(results: Dict[str, Any], filename: Optional[str] = None,
                             output_dir: str = "data/reports") -> str:
    """
    Export trade history to CSV

    Args:
        results: Backtest results dictionary
        filename: Output filename
        output_dir: Output directory

    Returns:
        Path to CSV file
    """
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        ticker = results.get('ticker', 'strategy')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{ticker}_trades_{timestamp}.csv"

    filepath = os.path.join(output_dir, filename)

    trades = results.get('trades', [])
    if trades:
        df = pd.DataFrame(trades)
        df.to_csv(filepath, index=False)

    return filepath

from typing import List, Dict, Any
import logging
import backtrader as bt

logger = logging.getLogger(__name__)


class TradeMarkerExtractor:
    """
    Extractor for trade markers (entry/exit points) from strategy trades.
    """

    @staticmethod
    def extract(strat: bt.Strategy) -> List[Dict[str, Any]]:
        """
        Extract trade markers from a strategy's trade history.

        Args:
            strat: Backtrader strategy instance with trades attribute

        Returns:
            Sorted list of trade markers with date, price, type, and action
        """
        markers = []

        if not hasattr(strat, 'trades'):
            return markers

        for trade in strat.trades:
            try:
                # Extract entry marker
                entry_marker = TradeMarkerExtractor._create_entry_marker(trade)
                if entry_marker:
                    markers.append(entry_marker)

                # Extract exit marker
                exit_marker = TradeMarkerExtractor._create_exit_marker(trade)
                if exit_marker:
                    markers.append(exit_marker)

            except (KeyError, AttributeError, ValueError) as e:
                logger.debug(f"Skipping malformed trade: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error extracting trade marker: {e}", exc_info=True)
                continue

        # Sort markers by date
        return sorted(markers, key=lambda x: x['date'])

    @staticmethod
    def _create_entry_marker(trade: Dict[str, Any]) -> Dict[str, Any]:
        """Create an entry trade marker"""
        entry_date = trade.get('entry_date')
        if entry_date is None:
            return None

        entry_date_str = TradeMarkerExtractor._format_date(entry_date)

        return {
            'date': entry_date_str,
            'price': float(trade['entry_price']),
            'type': 'BUY' if trade['type'] == 'LONG' else 'SELL',
            'action': 'OPEN'
        }

    @staticmethod
    def _create_exit_marker(trade: Dict[str, Any]) -> Dict[str, Any]:
        """Create an exit trade marker"""
        exit_date = trade.get('exit_date')
        if exit_date is None:
            return None

        exit_date_str = TradeMarkerExtractor._format_date(exit_date)

        return {
            'date': exit_date_str,
            'price': float(trade['exit_price']),
            'type': 'SELL' if trade['type'] == 'LONG' else 'BUY',
            'action': 'CLOSE',
            'pnl': float(trade['pnl'])
        }

    @staticmethod
    def _format_date(date_obj) -> str:
        """Format a date object to ISO string"""
        if hasattr(date_obj, 'isoformat'):
            return date_obj.isoformat()
        elif hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            return str(date_obj)

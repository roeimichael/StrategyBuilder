from typing import List, Dict, Any
import backtrader as bt

from .ohlc_extractor import OHLCExtractor
from .indicator_extractor import IndicatorExtractor
from .trade_marker_extractor import TradeMarkerExtractor


class ChartDataExtractor:
    """
    Orchestrator for extracting unified chart data.
    Combines OHLC data, technical indicators, and trade markers into a single timeline.
    """

    def __init__(self):
        self.ohlc_extractor = OHLCExtractor()
        self.indicator_extractor = IndicatorExtractor()
        self.trade_marker_extractor = TradeMarkerExtractor()

    def extract(self, strat: bt.Strategy, data_feed: bt.feeds.PandasData) -> List[Dict[str, Any]]:
        """
        Extract unified chart data containing OHLC, indicators, and trade markers.

        Args:
            strat: Backtrader strategy instance
            data_feed: Backtrader data feed

        Returns:
            List of unified data points, each containing:
            - date
            - OHLC data (open, high, low, close, volume)
            - indicators (dict of indicator values)
            - trade_markers (list of trades at this timestamp)
        """
        # Extract all components
        ohlc_data = self.ohlc_extractor.extract(data_feed)
        indicators = self.indicator_extractor.extract(strat, len(ohlc_data))
        trade_markers = self.trade_marker_extractor.extract(strat)

        # Group trade markers by date for efficient lookup
        trade_markers_by_date = self._group_markers_by_date(trade_markers)

        # Build unified timeline
        unified_data = self._build_unified_timeline(
            ohlc_data,
            indicators,
            trade_markers_by_date
        )

        return unified_data

    @staticmethod
    def _group_markers_by_date(markers: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Group trade markers by date for efficient lookup.

        Args:
            markers: List of trade markers

        Returns:
            Dictionary mapping dates to lists of markers
        """
        markers_by_date = {}

        for marker in markers:
            date = marker['date']
            if date not in markers_by_date:
                markers_by_date[date] = []

            markers_by_date[date].append({
                'type': marker['type'],
                'action': marker['action'],
                'price': marker['price'],
                'pnl': marker.get('pnl')
            })

        return markers_by_date

    @staticmethod
    def _build_unified_timeline(
        ohlc_data: List[Dict[str, Any]],
        indicators: Dict[str, List],
        trade_markers_by_date: Dict[str, List]
    ) -> List[Dict[str, Any]]:
        """
        Build unified timeline combining all data sources.

        Args:
            ohlc_data: List of OHLC data points
            indicators: Dictionary of indicator name to value lists
            trade_markers_by_date: Trade markers grouped by date

        Returns:
            Unified data points list
        """
        unified_data = []

        for i, ohlc in enumerate(ohlc_data):
            data_point = {
                'date': ohlc['date'],
                'open': ohlc['open'],
                'high': ohlc['high'],
                'low': ohlc['low'],
                'close': ohlc['close'],
                'volume': ohlc['volume'],
                'indicators': {},
                'trade_markers': trade_markers_by_date.get(ohlc['date'], [])
            }

            # Add indicator values for this timestamp
            for indicator_name, values in indicators.items():
                if i < len(values):
                    data_point['indicators'][indicator_name] = values[i]
                else:
                    data_point['indicators'][indicator_name] = None

            unified_data.append(data_point)

        return unified_data

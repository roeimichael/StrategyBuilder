from typing import List, Dict, Any
import backtrader as bt
from .ohlc_extractor import OHLCExtractor
from .indicator_extractor import IndicatorExtractor
from .trade_marker_extractor import TradeMarkerExtractor

class ChartDataExtractor:
    def __init__(self):
        self.ohlc_extractor = OHLCExtractor()
        self.indicator_extractor = IndicatorExtractor()
        self.trade_marker_extractor = TradeMarkerExtractor()

    def extract(self, strat: bt.Strategy, data_feed: bt.feeds.PandasData) -> List[Dict[str, Any]]:
        ohlc_data = self.ohlc_extractor.extract(data_feed)
        indicators = self.indicator_extractor.extract(strat, len(ohlc_data))
        trade_markers = self.trade_marker_extractor.extract(strat)
        trade_markers_by_date = self._group_markers_by_date(trade_markers)
        unified_data = self._build_unified_timeline(ohlc_data, indicators, trade_markers_by_date)
        return unified_data

    @staticmethod
    def _group_markers_by_date(markers: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
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
            for indicator_name, values in indicators.items():
                if i < len(values):
                    data_point['indicators'][indicator_name] = values[i]
                else:
                    data_point['indicators'][indicator_name] = None
            unified_data.append(data_point)
        return unified_data

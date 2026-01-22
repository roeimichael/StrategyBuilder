from typing import List, Dict, Any
import backtrader as bt


class OHLCExtractor:
    """
    Extractor for OHLC (Open, High, Low, Close, Volume) data from Backtrader data feeds.
    """

    @staticmethod
    def extract(data_feed: bt.feeds.PandasData) -> List[Dict[str, Any]]:
        """
        Extract OHLC data from a Backtrader data feed.

        Args:
            data_feed: Backtrader PandasData feed

        Returns:
            List of dictionaries containing OHLC data with timestamps
        """
        ohlc_list = []

        if not hasattr(data_feed, 'p') or not hasattr(data_feed.p, 'dataname'):
            return ohlc_list

        df = data_feed.p.dataname
        if df is None or df.empty:
            return ohlc_list

        for idx, row in df.iterrows():
            try:
                ohlc_list.append({
                    'date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'open': float(row.get('Open', row.get('open', 0))),
                    'high': float(row.get('High', row.get('high', 0))),
                    'low': float(row.get('Low', row.get('low', 0))),
                    'close': float(row.get('Close', row.get('close', 0))),
                    'volume': float(row.get('Volume', row.get('volume', 0)))
                })
            except Exception:
                # Skip malformed data points
                continue

        return ohlc_list

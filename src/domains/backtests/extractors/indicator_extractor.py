from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import logging
import backtrader as bt

logger = logging.getLogger(__name__)


class IndicatorValueExtractor(ABC):
    """Base class for extracting values from different indicator types"""

    @abstractmethod
    def can_extract(self, indicator) -> bool:
        """Check if this extractor can handle the given indicator"""
        pass

    @abstractmethod
    def extract(self, indicator, data_length: int) -> Dict[str, List]:
        """Extract values from the indicator"""
        pass


class ArrayBasedExtractor(IndicatorValueExtractor):
    """Extractor for indicators with direct array access"""

    def can_extract(self, indicator) -> bool:
        return hasattr(indicator, 'array') and not isinstance(indicator, bt.Indicator)

    def extract(self, indicator, data_length: int) -> Dict[str, List]:
        """Extract values from array-based indicator"""
        values = []
        arr = indicator.array

        for i in range(len(arr)):
            try:
                val = arr[i]
                if val is not None and not self._is_nan(val):
                    values.append(float(val))
                else:
                    values.append(None)
            except (IndexError, KeyError):
                values.append(None)

        return values

    @staticmethod
    def _is_nan(val) -> bool:
        """Check if value is NaN"""
        return isinstance(val, float) and (val != val)


class SingleLineIndicatorExtractor(IndicatorValueExtractor):
    """Extractor for Backtrader indicators with single line"""

    def can_extract(self, indicator) -> bool:
        if not isinstance(indicator, bt.Indicator):
            return False
        if not hasattr(indicator, 'lines'):
            return False

        line_names = indicator.getlinealiases()
        return len(line_names) == 1

    def extract(self, indicator, data_length: int) -> Dict[str, List]:
        """Extract values from single-line indicator"""
        line_names = indicator.getlinealiases()
        line = getattr(indicator.lines, line_names[0], None)

        if line is None or not hasattr(line, 'array'):
            return []

        return self._extract_line_values(line.array)

    @staticmethod
    def _extract_line_values(arr) -> List:
        """Extract values from a line array"""
        values = []
        for i in range(len(arr)):
            try:
                val = arr[i]
                if val is not None and not (isinstance(val, float) and (val != val)):
                    values.append(float(val))
                else:
                    values.append(None)
            except (IndexError, KeyError):
                values.append(None)
        return values


class MultiLineIndicatorExtractor(IndicatorValueExtractor):
    """Extractor for Backtrader indicators with multiple lines"""

    def can_extract(self, indicator) -> bool:
        if not isinstance(indicator, bt.Indicator):
            return False
        if not hasattr(indicator, 'lines'):
            return False

        line_names = indicator.getlinealiases()
        return len(line_names) > 1

    def extract(self, indicator, data_length: int) -> Dict[str, List]:
        """Extract values from multi-line indicator"""
        result = {}
        line_names = indicator.getlinealiases()

        for line_name in line_names:
            if not line_name:
                continue

            line = getattr(indicator.lines, line_name, None)
            if line is None or not hasattr(line, 'array'):
                continue

            result[line_name] = self._extract_line_values(line.array)

        return result

    @staticmethod
    def _extract_line_values(arr) -> List:
        """Extract values from a line array"""
        values = []
        for i in range(len(arr)):
            try:
                val = arr[i]
                if val is not None and not (isinstance(val, float) and (val != val)):
                    values.append(float(val))
                else:
                    values.append(None)
            except (IndexError, KeyError):
                values.append(None)
        return values


class IndicatorExtractor:
    """
    Main extractor for technical indicators from strategies.
    Uses strategy pattern to handle different indicator types.
    """

    def __init__(self):
        self.extractors = [
            ArrayBasedExtractor(),
            SingleLineIndicatorExtractor(),
            MultiLineIndicatorExtractor()
        ]

    def extract(self, strat: bt.Strategy, data_length: int) -> Dict[str, List]:
        """
        Extract all technical indicators from a strategy.

        Args:
            strat: Backtrader strategy instance
            data_length: Length of data for validation

        Returns:
            Dictionary mapping indicator names to value lists
        """
        indicators_data = {}

        # Try to get indicators from the strategy's get_technical_indicators method
        technical_indicators = self._get_technical_indicators(strat)

        if technical_indicators:
            indicators_data = self._extract_from_dict(technical_indicators, data_length)
        else:
            # Fallback: introspect strategy attributes for indicators
            indicators_data = self._extract_from_attributes(strat, data_length)

        return indicators_data

    def _get_technical_indicators(self, strat: bt.Strategy) -> Optional[Dict]:
        """Get indicators from strategy's method or attribute"""
        if hasattr(strat, 'get_technical_indicators') and callable(strat.get_technical_indicators):
            return strat.get_technical_indicators()
        elif hasattr(strat, 'technical_indicators') and isinstance(strat.technical_indicators, dict):
            return strat.technical_indicators
        return None

    def _extract_from_dict(self, indicators: Dict, data_length: int) -> Dict[str, List]:
        """Extract indicators from a dictionary of indicator objects"""
        result = {}

        for indicator_name, indicator_obj in indicators.items():
            if indicator_obj is None:
                continue

            try:
                extracted = self._extract_single_indicator(
                    indicator_name,
                    indicator_obj,
                    data_length
                )
                result.update(extracted)
            except (AttributeError, IndexError, ValueError) as e:
                logger.debug(f"Failed to extract indicator '{indicator_name}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error extracting indicator '{indicator_name}': {e}", exc_info=True)
                continue

        return result

    def _extract_from_attributes(self, strat: bt.Strategy, data_length: int) -> Dict[str, List]:
        """Extract indicators by introspecting strategy attributes"""
        result = {}

        for attr_name in dir(strat):
            if attr_name.startswith('_'):
                continue

            attr = getattr(strat, attr_name, None)
            if attr is None or not isinstance(attr, bt.Indicator):
                continue

            try:
                extracted = self._extract_single_indicator(
                    attr_name,
                    attr,
                    data_length
                )
                result.update(extracted)
            except (AttributeError, IndexError, ValueError) as e:
                logger.debug(f"Failed to extract indicator attribute '{attr_name}': {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error extracting indicator attribute '{attr_name}': {e}", exc_info=True)
                continue

        return result

    def _extract_single_indicator(
        self,
        name: str,
        indicator,
        data_length: int
    ) -> Dict[str, List]:
        """Extract a single indicator using the appropriate extractor"""
        for extractor in self.extractors:
            if extractor.can_extract(indicator):
                values = extractor.extract(indicator, data_length)

                # Handle both single values and multi-line results
                if isinstance(values, dict):
                    # Multi-line indicator
                    return {f"{name}_{line_name}": line_values
                            for line_name, line_values in values.items()}
                else:
                    # Single value or list
                    return {name: values}

        return {}

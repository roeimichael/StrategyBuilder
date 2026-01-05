#!/usr/bin/env python3
"""
Comprehensive test to verify all strategies return proper technical indicators
"""
import requests
import json
from typing import Dict, List

API_URL = "http://localhost:8086"

# Define all strategies with their expected indicators
STRATEGIES = {
    "alligator_strategy": {
        "expected_indicators": [
            'Alligator_Lips_SMA5',
            'Alligator_Teeth_SMA8',
            'Alligator_Jaws_SMA13',
            'EMA_200'
        ],
        "start_date": "2024-01-01",  # Needs longer period for 200-EMA
    },
    "bollinger_bands_strategy": {
        "expected_indicators": [
            'Bollinger_Upper',
            'Bollinger_Middle',
            'Bollinger_Lower'
        ],
        "start_date": "2025-01-01",
    },
    "adx_strategy": {
        "expected_indicators": [
            'ADX',
            'SMA_20',
            'SMA_50',
            'Bollinger_Upper',
            'Bollinger_Middle',
            'Bollinger_Lower'
        ],
        "start_date": "2025-01-01",
    },
    "williams_r_strategy": {
        "expected_indicators": [
            'Williams_R'
        ],
        "start_date": "2025-01-01",
    },
    "mfi_strategy": {
        "expected_indicators": [
            'MFI'
        ],
        "start_date": "2025-01-01",
    },
    "rsi_stochastic_strategy": {
        "expected_indicators": [
            'RSI',
            'Stochastic_K',
            'Stochastic_D'
        ],
        "start_date": "2025-01-01",
    },
    "cci_atr_strategy": {
        "expected_indicators": [
            'CCI',
            'ATR'
        ],
        "start_date": "2025-01-01",
    },
    "keltner_channel_strategy": {
        "expected_indicators": [
            'EMA',
            'ATR',
            'Keltner_Upper',
            'Keltner_Lower'
        ],
        "start_date": "2025-01-01",
    },
    "tema_crossover_strategy": {
        "expected_indicators": [
            'Volume_SMA',
            'TEMA_20',
            'TEMA_60'
        ],
        "start_date": "2025-01-01",
    },
    "tema_macd_strategy": {
        "expected_indicators": [
            'MACD',
            'MACD_Signal',
            'MACD_Histogram',
            'TEMA_Open',
            'TEMA_Close'
        ],
        "start_date": "2025-01-01",
    },
    "momentum_multi_strategy": {
        "expected_indicators": [
            'ROC',
            'RSI',
            'OBV'
        ],
        "start_date": "2025-01-01",
    },
    "cmf_atr_macd_strategy": {
        "expected_indicators": [
            'MACD',
            'MACD_Signal',
            'MACD_Histogram',
            'ATR',
            'CMF'
        ],
        "start_date": "2025-01-01",
    },
}


def test_strategy(strategy_name: str, config: Dict) -> Dict:
    """Test a single strategy and return results"""
    print(f"\n{'='*80}")
    print(f"Testing: {strategy_name}")
    print(f"{'='*80}")

    # Run backtest
    response = requests.post(
        f"{API_URL}/backtest",
        json={
            "ticker": "AAPL",
            "strategy": strategy_name,
            "start_date": config["start_date"],
            "end_date": "2026-01-05",
            "interval": "1d",
            "cash": 10000.0
        }
    )

    result = {
        "strategy": strategy_name,
        "status": "failed",
        "indicators_found": [],
        "missing_indicators": [],
        "unexpected_indicators": [],
        "error": None
    }

    # Check response
    if response.status_code != 200:
        result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
        print(f"❌ Error: {result['error']}")
        return result

    data = response.json()

    # Check chart_data exists
    if 'chart_data' not in data:
        result["error"] = "No chart_data in response"
        print(f"❌ {result['error']}")
        return result

    chart_data = data['chart_data']
    indicators = chart_data.get('indicators', {})

    if not indicators:
        result["error"] = "No indicators in chart_data"
        print(f"❌ {result['error']}")
        return result

    # Analyze indicators
    expected = set(config["expected_indicators"])
    found = set(indicators.keys())

    result["indicators_found"] = list(found)
    result["missing_indicators"] = list(expected - found)
    result["unexpected_indicators"] = list(found - expected)

    # Print results
    print(f"✓ Received {len(chart_data.get('ohlc', []))} OHLC bars")
    print(f"\n📊 Technical Indicators:")
    print("-" * 80)

    for indicator_name in sorted(indicators.keys()):
        num_values = len(indicators[indicator_name])
        non_null_count = sum(1 for v in indicators[indicator_name] if v is not None)
        is_expected = "✓" if indicator_name in expected else "⚠"
        print(f"  {is_expected} {indicator_name}: {num_values} values ({non_null_count} non-null)")

    # Check coverage
    print(f"\n📋 Expected Indicators Coverage:")
    print("-" * 80)
    all_found = True
    for exp in config["expected_indicators"]:
        if exp in indicators:
            print(f"  ✓ {exp}")
        else:
            print(f"  ❌ {exp} - MISSING")
            all_found = False

    if result["unexpected_indicators"]:
        print(f"\n⚠ Unexpected Indicators:")
        for ind in result["unexpected_indicators"]:
            print(f"  • {ind}")

    # Determine status
    if all_found and not result["missing_indicators"]:
        result["status"] = "passed"
        print(f"\n✅ PASSED - All expected indicators present")
    else:
        result["status"] = "partial"
        print(f"\n⚠ PARTIAL - Some indicators missing")

    return result


def main():
    """Run tests for all strategies"""
    print("=" * 80)
    print("COMPREHENSIVE STRATEGY INDICATOR TEST")
    print("Testing all 12 strategies for proper technical indicator exposure")
    print("=" * 80)

    results = []
    passed = 0
    failed = 0
    partial = 0

    # Test each strategy
    for strategy_name, config in STRATEGIES.items():
        try:
            result = test_strategy(strategy_name, config)
            results.append(result)

            if result["status"] == "passed":
                passed += 1
            elif result["status"] == "partial":
                partial += 1
            else:
                failed += 1

        except Exception as e:
            print(f"❌ Exception testing {strategy_name}: {e}")
            results.append({
                "strategy": strategy_name,
                "status": "failed",
                "error": str(e)
            })
            failed += 1

    # Print summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Strategies: {len(STRATEGIES)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠ Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print("=" * 80)

    # Detailed breakdown
    print("\nDetailed Results:")
    print("-" * 80)
    for result in results:
        status_symbol = "✅" if result["status"] == "passed" else "⚠" if result["status"] == "partial" else "❌"
        print(f"{status_symbol} {result['strategy']}: {result['status'].upper()}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
        if result.get("missing_indicators"):
            print(f"   Missing: {', '.join(result['missing_indicators'])}")

    # Save results to JSON
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(STRATEGIES),
                "passed": passed,
                "partial": partial,
                "failed": failed
            },
            "results": results
        }, f, indent=2)

    print(f"\n📄 Results saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

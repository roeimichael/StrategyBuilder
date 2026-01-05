#!/usr/bin/env python3
"""
Quick test to verify alligator_strategy returns clean indicator names
"""
import requests
import json

API_URL = "http://localhost:8086"

def test_alligator_indicators():
    print("Testing Alligator Strategy Indicators...")
    print("=" * 80)

    # Run backtest with alligator strategy
    response = requests.post(
        f"{API_URL}/backtest",
        json={
            "ticker": "AAPL",
            "strategy": "alligator_strategy",
            "start_date": "2025-10-01",
            "end_date": "2026-01-05",
            "interval": "1d",
            "cash": 10000.0
        }
    )

    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return

    data = response.json()

    # Check chart_data exists
    if 'chart_data' not in data:
        print("❌ No chart_data in response")
        return

    chart_data = data['chart_data']
    indicators = chart_data.get('indicators', {})

    print(f"✓ Received {len(chart_data.get('ohlc', []))} OHLC bars")
    print(f"\n📊 Technical Indicators Returned:")
    print("-" * 80)

    for indicator_name in indicators.keys():
        num_values = len(indicators[indicator_name])
        non_null_count = sum(1 for v in indicators[indicator_name] if v is not None)
        print(f"  • {indicator_name}: {num_values} values ({non_null_count} non-null)")

    print("\n" + "=" * 80)

    # Expected indicators for alligator strategy
    expected_indicators = [
        'Alligator_Lips_SMA5',
        'Alligator_Teeth_SMA8',
        'Alligator_Jaws_SMA13',
        'EMA_200'
    ]

    print("\n✓ Expected Indicators:")
    for exp in expected_indicators:
        if exp in indicators:
            print(f"  ✓ {exp} - FOUND")
        else:
            print(f"  ❌ {exp} - MISSING")

    # Check for unwanted indicators (like cross_lips)
    unwanted = ['cross_lips', 'crossover']
    print("\n✓ Unwanted Indicators (should NOT be present):")
    for unwanted_name in unwanted:
        found = any(unwanted_name in ind.lower() for ind in indicators.keys())
        if not found:
            print(f"  ✓ {unwanted_name} - NOT PRESENT (good)")
        else:
            print(f"  ❌ {unwanted_name} - PRESENT (should be excluded)")

    print("\n" + "=" * 80)
    print("\n📄 Full indicator response:")
    print(json.dumps(indicators, indent=2)[:500] + "...")

if __name__ == "__main__":
    try:
        test_alligator_indicators()
    except Exception as e:
        print(f"❌ Test failed: {e}")

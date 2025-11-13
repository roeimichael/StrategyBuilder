"""
Simple test to verify MultiIndex column fix
Tests the core issue without needing full dependencies
"""
import pandas as pd
import datetime

# Simulate what yfinance 0.2.31+ returns (MultiIndex columns)
data = pd.DataFrame({
    ('Open', 'AAPL'): [150.0, 152.0, 151.0],
    ('High', 'AAPL'): [153.0, 154.0, 153.0],
    ('Low', 'AAPL'): [149.0, 151.0, 150.0],
    ('Close', 'AAPL'): [152.0, 151.5, 152.5],
    ('Volume', 'AAPL'): [1000000, 1100000, 1050000]
}, index=pd.date_range('2025-01-01', periods=3))

print("Original DataFrame columns (MultiIndex):")
print(f"  Type: {type(data.columns)}")
print(f"  Columns: {data.columns.tolist()}")
print(f"  Is MultiIndex: {isinstance(data.columns, pd.MultiIndex)}")

# Apply the fix from run_strategy.py
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
    print("\n✓ Applied MultiIndex flattening")

# Ensure all column names are strings (handle any remaining tuples)
if len(data.columns) > 0 and isinstance(data.columns[0], tuple):
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    print("✓ Applied tuple to string conversion")

print("\nFixed DataFrame columns:")
print(f"  Type: {type(data.columns)}")
print(f"  Columns: {data.columns.tolist()}")
print(f"  Is MultiIndex: {isinstance(data.columns, pd.MultiIndex)}")

# Test that .lower() works on all columns (what backtrader tries to do)
try:
    colnames = [x.lower() for x in data.columns.values]
    print(f"\n✅ SUCCESS: Column names can be lowercased: {colnames}")
    print("\nThe MultiIndex fix is working correctly!")
except AttributeError as e:
    print(f"\n❌ FAILED: {e}")
    print("The fix did not work properly")

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports from project root...")
print("-" * 50)

try:
    print("1. Testing config import...")
    from config import Config
    print(f"   ✓ Config imported: {Config.API_TITLE}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("2. Testing core imports...")
    from core import Run_strategy, Strategy_skeleton, DataManager
    print(f"   ✓ Core modules imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("3. Testing utils import...")
    from utils import PerformanceAnalyzer
    print(f"   ✓ Utils imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("4. Testing strategies import...")
    from strategies import Bollinger_three, TEMA_MACD
    print(f"   ✓ Strategies imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("5. Testing indicators import...")
    from indicators import CMF, MFI, OBV
    print(f"   ✓ Indicators imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("6. Testing API import...")
    from api.main import app
    print(f"   ✓ API imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("-" * 50)
print("Import verification complete!")

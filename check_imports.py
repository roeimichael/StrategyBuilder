"""
Quick diagnostic script to check if all imports are working correctly.
Run this before starting the API server to verify everything is set up properly.
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return status."""
    path = Path(filepath)
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    return exists, size

def test_import(module_path, item_name):
    """Test importing a specific item from a module."""
    try:
        parts = module_path.rsplit('.', 1)
        if len(parts) == 2:
            module_name, _ = parts
            module = __import__(module_path, fromlist=[item_name])
            item = getattr(module, item_name, None)
            if item is None:
                return False, f"'{item_name}' not found in module"
            return True, "OK"
        else:
            __import__(module_path)
            return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Import Diagnostics for StrategyBuilder")
    print("=" * 70)
    print()

    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ ERROR: Not in project root directory!")
        print("   Please run this from: C:\\Users\\roeym\\Desktop\\projects\\StrategyBuilder")
        return 1

    # Check critical files
    print("📁 Checking critical files...")
    files_to_check = [
        "src/api/models/__init__.py",
        "src/api/models/requests.py",
        "src/api/models/responses.py",
        "src/data/__init__.py",
        "src/data/run_repository.py",
        "src/services/backtest_service.py",
        "src/__init__.py",
    ]

    all_exist = True
    for filepath in files_to_check:
        exists, size = check_file_exists(filepath)
        status = "✓" if exists else "✗"
        size_str = f"({size} bytes)" if exists else "(MISSING)"
        print(f"   {status} {filepath} {size_str}")
        if not exists:
            all_exist = False

    print()

    if not all_exist:
        print("❌ Some files are missing! Please pull from git:")
        print("   git pull origin claude/add-persistent-run-storage-tSepA")
        return 1

    # Test imports
    print("🔍 Testing imports...")
    imports_to_test = [
        ("src.api.models", "BacktestRequest"),
        ("src.api.models", "MarketDataRequest"),
        ("src.api.models", "OptimizationRequest"),
        ("src.api.models", "ReplayRunRequest"),
        ("src.api.models", "BacktestResponse"),
        ("src.api.models", "SavedRunSummaryResponse"),
        ("src.api.models", "SavedRunDetailResponse"),
    ]

    all_imports_ok = True
    for module, item in imports_to_test:
        success, message = test_import(module, item)
        status = "✓" if success else "✗"
        detail = "" if success else f" - {message}"
        print(f"   {status} from {module} import {item}{detail}")
        if not success:
            all_imports_ok = False

    print()

    # Check for cache files that might cause issues
    print("🗑️  Checking for cache files...")
    cache_dirs = list(Path(".").rglob("__pycache__"))
    pyc_files = list(Path(".").rglob("*.pyc"))

    if cache_dirs or pyc_files:
        print(f"   Found {len(cache_dirs)} __pycache__ directories")
        print(f"   Found {len(pyc_files)} .pyc files")
        print()
        print("   ⚠️  Cache files may cause import issues. To clear them:")
        print("   Windows: run fix_imports.bat")
        print("   Linux/Mac: run bash fix_imports.sh")
    else:
        print("   ✓ No cache files found")

    print()
    print("=" * 70)

    if all_imports_ok:
        print("✅ All imports working correctly!")
        print("=" * 70)
        print()
        print("You can now start the API server:")
        print("   python run_api.py")
        return 0
    else:
        print("❌ Some imports failed!")
        print("=" * 70)
        print()
        print("Troubleshooting steps:")
        print("1. Clear Python cache:")
        print("   Windows: run fix_imports.bat")
        print("   Linux/Mac: bash fix_imports.sh")
        print()
        print("2. Verify you pulled latest changes:")
        print("   git pull origin claude/add-persistent-run-storage-tSepA")
        print()
        print("3. Check Python version (requires 3.8+):")
        print("   python --version")
        print()
        print("4. Verify virtual environment is activated")
        return 1

if __name__ == "__main__":
    sys.exit(main())

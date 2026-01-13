"""
Comprehensive verification script to diagnose import issues.
Run this on Windows to see exactly what's wrong.
"""

import sys
import os
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_file_content(filepath, class_names):
    """Check if specific classes are defined in a file."""
    path = Path(filepath)
    if not path.exists():
        return False, "File does not exist"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        missing = []
        for class_name in class_names:
            if f"class {class_name}" not in content:
                missing.append(class_name)

        if missing:
            return False, f"Missing classes: {', '.join(missing)}"
        return True, "All classes found"
    except Exception as e:
        return False, str(e)

def main():
    print_section("StrategyBuilder Import Diagnostics")

    # Check current directory
    if not Path("src").exists():
        print("\n❌ ERROR: Not in project root directory!")
        print("Current directory:", os.getcwd())
        print("\nPlease cd to your project root:")
        print("  cd C:\\Users\\roeym\\Desktop\\projects\\StrategyBuilder")
        return 1

    print("\n✓ In project root directory")
    print("  Path:", os.getcwd())

    # Check critical files exist
    print_section("File Existence Check")

    critical_files = {
        "src/api/models/__init__.py": [],
        "src/api/models/requests.py": ["BacktestRequest", "MarketDataRequest", "OptimizationRequest", "ReplayRunRequest"],
        "src/api/models/responses.py": ["BacktestResponse", "SavedRunSummaryResponse", "SavedRunDetailResponse"],
        "src/exceptions/__init__.py": [],
        "src/exceptions/strategy_errors.py": ["StrategyNotFoundError", "StrategyLoadError"],
    }

    all_files_ok = True
    for filepath, classes in critical_files.items():
        path = Path(filepath)
        if path.exists():
            size = path.stat().st_size
            print(f"\n✓ {filepath}")
            print(f"  Size: {size} bytes")

            if classes:
                success, message = check_file_content(filepath, classes)
                if success:
                    print(f"  ✓ {message}")
                else:
                    print(f"  ✗ {message}")
                    all_files_ok = False
        else:
            print(f"\n✗ {filepath} - MISSING!")
            all_files_ok = False

    if not all_files_ok:
        print("\n❌ Some files are missing or incomplete!")
        print("\nFix by running:")
        print("  git pull origin claude/add-persistent-run-storage-tSepA")
        return 1

    # Check what's actually exported from models/__init__.py
    print_section("Models __init__.py Export Check")

    try:
        with open("src/api/models/__init__.py", 'r', encoding='utf-8') as f:
            content = f.read()

        print("\nFile content:")
        print("-" * 70)
        for i, line in enumerate(content.split('\n'), 1):
            print(f"{i:3}: {line}")
        print("-" * 70)

        # Check for specific imports
        required_imports = [
            "BacktestRequest",
            "MarketDataRequest",
            "OptimizationRequest",
            "ReplayRunRequest",
            "BacktestResponse",
            "SavedRunSummaryResponse",
            "SavedRunDetailResponse",
            "StrategyInfo",
            "StrategyParameters",
        ]

        print("\nChecking for required imports in __all__:")
        all_present = True
        for name in required_imports:
            if f"'{name}'" in content or f'"{name}"' in content:
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} - NOT FOUND!")
                all_present = False

        if not all_present:
            print("\n❌ Some imports are missing from __all__!")
            return 1

    except Exception as e:
        print(f"\n✗ Error reading file: {e}")
        return 1

    # Check for __pycache__ directories
    print_section("Python Cache Check")

    pycache_dirs = list(Path(".").rglob("__pycache__"))
    pyc_files = list(Path(".").rglob("*.pyc"))

    if pycache_dirs or pyc_files:
        print(f"\n⚠️  Found {len(pycache_dirs)} __pycache__ directories")
        print(f"⚠️  Found {len(pyc_files)} .pyc files")
        print("\nOld cache files can cause import errors!")
        print("\nTo clear cache, run:")
        print("  fix_imports.bat  (on Windows)")
        print("  bash fix_imports.sh  (on Linux/Mac)")
        print("\nOr manually delete:")
        if pycache_dirs:
            for d in pycache_dirs[:5]:  # Show first 5
                print(f"  - {d}")
            if len(pycache_dirs) > 5:
                print(f"  ... and {len(pycache_dirs) - 5} more")
    else:
        print("\n✓ No cache files found")

    # Final summary
    print_section("Summary")

    print("\n✅ All files exist and have correct content")
    print("✅ All required classes are defined")
    print("✅ Models __init__.py exports all required items")

    if pycache_dirs or pyc_files:
        print("\n⚠️  Python cache exists - recommend clearing it")
        print("\nNext steps:")
        print("  1. Run: fix_imports.bat")
        print("  2. Then: python run_api.py")
    else:
        print("\n✅ No cache issues detected")
        print("\nYou should be able to start the server:")
        print("  python run_api.py")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

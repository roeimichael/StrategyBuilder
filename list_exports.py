"""
Simple script to list what's actually being exported from modules.
This helps verify the imports are working correctly.
"""

import sys
import ast
from pathlib import Path

def get_exports_from_file(filepath):
    """Parse a Python file and extract what's in __all__."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            return [elt.s if isinstance(elt, ast.Str) else elt.value
                                    for elt in node.value.elts]
        return []
    except Exception as e:
        return [f"Error: {e}"]

def get_classes_from_file(filepath):
    """Parse a Python file and extract class names."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())

        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        return classes
    except Exception as e:
        return [f"Error: {e}"]

def main():
    print("=" * 70)
    print("Module Export Analysis")
    print("=" * 70)

    # Check models module
    print("\n📦 src/api/models/__init__.py")
    print("-" * 70)
    exports = get_exports_from_file("src/api/models/__init__.py")
    if exports:
        print("Exports (__all__):")
        for item in exports:
            print(f"  - {item}")
    else:
        print("  No __all__ found or error reading file")

    # Check requests.py
    print("\n📦 src/api/models/requests.py")
    print("-" * 70)
    classes = get_classes_from_file("src/api/models/requests.py")
    if classes:
        print("Classes defined:")
        for cls in classes:
            print(f"  - {cls}")
    else:
        print("  No classes found or error reading file")

    # Check responses.py
    print("\n📦 src/api/models/responses.py")
    print("-" * 70)
    classes = get_classes_from_file("src/api/models/responses.py")
    if classes:
        print("Classes defined:")
        for cls in classes:
            print(f"  - {cls}")
    else:
        print("  No classes found or error reading file")

    # Check exceptions
    print("\n📦 src/exceptions/__init__.py")
    print("-" * 70)
    exports = get_exports_from_file("src/exceptions/__init__.py")
    if exports:
        print("Exports (__all__):")
        for item in exports:
            print(f"  - {item}")
    else:
        print("  No __all__ found or error reading file")

    # Cross-check: are all classes in requests.py exported?
    print("\n" + "=" * 70)
    print("Cross-Check: Requests")
    print("=" * 70)

    requests_classes = get_classes_from_file("src/api/models/requests.py")
    models_exports = get_exports_from_file("src/api/models/__init__.py")

    for cls in requests_classes:
        if cls in models_exports:
            print(f"✓ {cls} is exported")
        else:
            print(f"✗ {cls} is NOT exported (should be in __all__)")

    # Cross-check: are all classes in responses.py exported?
    print("\n" + "=" * 70)
    print("Cross-Check: Responses")
    print("=" * 70)

    responses_classes = get_classes_from_file("src/api/models/responses.py")

    for cls in responses_classes:
        if cls in models_exports:
            print(f"✓ {cls} is exported")
        else:
            print(f"✗ {cls} is NOT exported (should be in __all__)")

    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)

    # Summary
    all_good = True
    missing = []

    required = ["ReplayRunRequest", "SavedRunSummaryResponse", "SavedRunDetailResponse"]
    for item in required:
        if item not in models_exports:
            all_good = False
            missing.append(item)

    if all_good:
        print("\n✅ All required models are properly exported")
    else:
        print(f"\n❌ Missing exports: {', '.join(missing)}")
        print("\nThe __init__.py file needs to be updated!")

    return 0 if all_good else 1

if __name__ == "__main__":
    try:
        if not Path("src").exists():
            print("❌ Error: Not in project root directory")
            print(f"Current directory: {Path.cwd()}")
            sys.exit(1)

        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

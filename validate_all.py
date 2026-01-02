import sys
import os
import py_compile

print("="*60)
print("VALIDATING ALL PYTHON FILES")
print("="*60)

errors = []
success = []

# Get all Python files
for root, dirs, files in os.walk('src'):
    # Skip __pycache__
    dirs[:] = [d for d in dirs if d != '__pycache__']
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                py_compile.compile(filepath, doraise=True)
                success.append(filepath)
                print(f"✓ {filepath}")
            except py_compile.PyCompileError as e:
                errors.append((filepath, str(e)))
                print(f"✗ {filepath}")
                print(f"  Error: {e}")

print("\n" + "="*60)
print("VALIDATION SUMMARY")
print("="*60)
print(f"Total files: {len(success) + len(errors)}")
print(f"Valid: {len(success)}")
print(f"Errors: {len(errors)}")

if errors:
    print("\nFiles with errors:")
    for filepath, error in errors:
        print(f"  - {filepath}")
else:
    print("\n✓ All files are valid!")

# Validate runner scripts
print("\n" + "="*60)
print("VALIDATING RUNNER SCRIPTS")
print("="*60)

runner_files = ['run_api.py', 'test_api.py', 'verify_imports.py']
for file in runner_files:
    if os.path.exists(file):
        try:
            py_compile.compile(file, doraise=True)
            print(f"✓ {file}")
        except Exception as e:
            print(f"✗ {file}: {e}")
    else:
        print(f"⚠ {file} not found")


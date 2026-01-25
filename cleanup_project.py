"""Comprehensive cleanup script for StrategyBuilder project."""
import os
import re
from pathlib import Path
from typing import List, Tuple

def clean_file(file_path: Path) -> Tuple[bool, str]:
    """Clean a single Python file according to project standards."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    changes = []

    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\u2600-\u26FF"
        u"\u2700-\u27BF"
        "✓✗⚠"
        "]+", flags=re.UNICODE)

    if emoji_pattern.search(content):
        content = content.replace('✓', 'PASS')
        content = content.replace('✗', 'FAIL')
        content = content.replace('⚠', 'WARN')
        content = emoji_pattern.sub('', content)
        changes.append("Removed emojis")

    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    # Remove trailing whitespace
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f"{file_path}: {', '.join(changes) if changes else 'Whitespace cleaned'}"
    return False, ""

def clean_source_files(directory: Path, exclude_patterns: List[str] = None) -> List[str]:
    """Clean all Python source files in directory."""
    exclude_patterns = exclude_patterns or ['__pycache__', '.git', 'venv', 'env']
    results = []

    for py_file in directory.rglob('*.py'):
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        modified, msg = clean_file(py_file)
        if modified:
            results.append(msg)

    return results

if __name__ == "__main__":
    print("Starting comprehensive project cleanup...")
    print("="*80)

    src_dir = Path('./src')
    test_dir = Path('./tests')

    print("\nCleaning source files...")
    src_results = clean_source_files(src_dir)
    for result in src_results:
        print(f"  {result}")

    print(f"\nSource files cleaned: {len(src_results)}")

    print("\nCleaning test files...")
    test_results = clean_source_files(test_dir)
    for result in test_results:
        print(f"  {result}")

    print(f"\nTest files cleaned: {len(test_results)}")

    print("\n" + "="*80)
    print(f"Total files cleaned: {len(src_results) + len(test_results)}")
    print("Cleanup complete!")

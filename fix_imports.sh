#!/bin/bash
echo "Fixing import cache issues..."
echo

echo "Step 1: Pulling latest changes from git..."
git pull origin claude/add-persistent-run-storage-tSepA
echo

echo "Step 2: Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✓ Cache cleared"
echo

echo "Step 3: Verifying files exist..."
[ -f "src/api/models/requests.py" ] && echo "✓ src/api/models/requests.py exists" || echo "✗ src/api/models/requests.py NOT FOUND!"
[ -f "src/api/models/responses.py" ] && echo "✓ src/api/models/responses.py exists" || echo "✗ src/api/models/responses.py NOT FOUND!"
[ -f "src/api/models/__init__.py" ] && echo "✓ src/api/models/__init__.py exists" || echo "✗ src/api/models/__init__.py NOT FOUND!"
[ -f "src/data/run_repository.py" ] && echo "✓ src/data/run_repository.py exists" || echo "✗ src/data/run_repository.py NOT FOUND!"
echo

echo "Step 4: Testing imports..."
python3 -c "from src.api.models import ReplayRunRequest; print('✓ ReplayRunRequest imported successfully')" 2>/dev/null || {
    echo "✗ Failed to import ReplayRunRequest"
    echo
    echo "Trying alternative import test..."
    python3 -c "import sys; sys.path.insert(0, '.'); from src.api.models.requests import ReplayRunRequest; print('✓ Direct import works')"
}
echo

echo "Done! Try starting the server now:"
echo "  python run_api.py"
echo

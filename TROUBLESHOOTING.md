# Troubleshooting Import Errors

## Problem: ImportError: cannot import name 'ReplayRunRequest'

This error occurs when Python's bytecode cache (.pyc files) is out of sync with the source files.

## Quick Fix (Choose One)

### Option 1: Automated Fix (Recommended)

**On Windows:**
```cmd
git pull origin claude/add-persistent-run-storage-tSepA
fix_imports.bat
```

**On Linux/Mac:**
```bash
git pull origin claude/add-persistent-run-storage-tSepA
bash fix_imports.sh
```

### Option 2: Manual Fix

1. **Pull latest changes:**
   ```bash
   git pull origin claude/add-persistent-run-storage-tSepA
   ```

2. **Clear Python cache:**

   **Windows (PowerShell):**
   ```powershell
   Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
   Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force
   ```

   **Windows (Command Prompt):**
   ```cmd
   for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
   del /s /q *.pyc
   ```

   **Linux/Mac:**
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   ```

3. **Verify imports:**
   ```bash
   python check_imports.py
   ```

4. **Restart the server:**
   ```bash
   python run_api.py
   ```

## Verify Everything is Working

Run the diagnostic script:
```bash
python check_imports.py
```

This will check:
- ✓ All required files exist
- ✓ All imports can be loaded
- ✓ No cache conflicts

If you see "✅ All imports working correctly!" you're good to go!

## Common Issues

### Issue: Files are missing

**Solution:** Pull from git again
```bash
git fetch origin
git checkout claude/add-persistent-run-storage-tSepA
git pull origin claude/add-persistent-run-storage-tSepA
```

### Issue: Virtual environment not activated

**Solution:** Activate your virtual environment

**Windows:**
```cmd
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Issue: Python version

**Check version:**
```bash
python --version
```

**Required:** Python 3.8 or higher

### Issue: Still getting import errors after clearing cache

**Solution:** Restart your IDE/terminal completely

1. Close your IDE (VSCode, PyCharm, etc.)
2. Close all terminal windows
3. Reopen and try again

## Files Added in This Update

The following new files were added:

### Core Implementation
- `src/data/run_repository.py` - Repository for storing backtest runs
- `src/data/__init__.py` - Data module initialization

### API Models
- Updates to `src/api/models/requests.py` - Added `ReplayRunRequest`
- Updates to `src/api/models/responses.py` - Added `SavedRunSummaryResponse`, `SavedRunDetailResponse`

### API Endpoints
- Updates to `src/api/main.py` - Added 3 new endpoints for saved runs

### Configuration
- Updates to `src/config/constants.py` - Added table name constants

### Services
- Updates to `src/services/backtest_service.py` - Integrated run storage

## New Endpoints Available

Once the import error is fixed, these endpoints will be available:

1. **GET /runs** - List all saved runs
2. **GET /runs/{run_id}** - Get details of a specific run
3. **POST /runs/{run_id}/replay** - Replay a saved run with optional overrides

## Need More Help?

If you're still experiencing issues after trying these steps:

1. Check the error message carefully
2. Verify you're in the correct directory
3. Make sure your virtual environment is activated
4. Try completely removing and recreating your virtual environment:
   ```bash
   rm -rf .venv  # or rmdir /s .venv on Windows
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

5. Check the output of `check_imports.py` for specific guidance

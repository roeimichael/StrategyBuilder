# Fix for Windows Import Errors

## ✅ Repository Status: VERIFIED CORRECT

I've verified that **ALL files in the repository are correct**:

```
✓ src/api/models/__init__.py - Properly exports all models
✓ src/api/models/requests.py - ReplayRunRequest is defined
✓ src/api/models/responses.py - SavedRunSummaryResponse and SavedRunDetailResponse are defined
✓ src/exceptions/ - All exception classes exist and are properly exported
```

## 🔍 Your Issue

You mentioned:
1. ❌ "models/__init__.py script in the api folder is not updated"
2. ❌ "exception folder doesn't even exists"

**Both of these are FALSE in the repository!** The files exist and are correct.

This means your local Windows copy is **out of sync** with the repository.

## 🚀 Fix Steps (Run These on Windows)

### Step 1: Pull Latest Changes

Open Command Prompt or PowerShell in your project directory and run:

```cmd
cd C:\Users\roeym\Desktop\projects\StrategyBuilder
git fetch origin
git pull origin claude/add-persistent-run-storage-tSepA
```

### Step 2: Verify Files Exist

Run this diagnostic script:

```cmd
python list_exports.py
```

**Expected output:**
```
✅ All required models are properly exported
```

If you see errors, the files didn't pull correctly. Try:

```cmd
git status
git reset --hard origin/claude/add-persistent-run-storage-tSepA
git pull origin claude/add-persistent-run-storage-tSepA
```

### Step 3: Clear Python Cache

Windows has aggressive Python bytecode caching. Clear it:

**Option A: Use the automated script**
```cmd
fix_imports.bat
```

**Option B: Manual clearing (PowerShell)**
```powershell
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force
```

**Option C: Manual clearing (Command Prompt)**
```cmd
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc
```

### Step 4: Run Comprehensive Diagnostics

```cmd
python diagnose_imports.py
```

This will show you:
- ✓ Which files exist
- ✓ What classes are defined
- ✓ What's being exported
- ⚠️ Any cache issues

### Step 5: Test Import

```cmd
python -c "from src.api.models import ReplayRunRequest, SavedRunSummaryResponse; print('SUCCESS: All imports work!')"
```

If this works, you're good to go!

### Step 6: Start Server

```cmd
python run_api.py
```

## 📋 What Should Exist

After pulling, you should have these files:

### Models
```
src/api/models/__init__.py       ← Exports all models
src/api/models/requests.py       ← Contains ReplayRunRequest
src/api/models/responses.py      ← Contains SavedRunSummaryResponse, SavedRunDetailResponse
```

### Exceptions
```
src/exceptions/__init__.py       ← Exports all exceptions
src/exceptions/base.py           ← StrategyBuilderError
src/exceptions/strategy_errors.py ← StrategyNotFoundError, StrategyLoadError
src/exceptions/data_errors.py    ← DataFetchError, etc.
```

### Data Module
```
src/data/__init__.py
src/data/run_repository.py       ← RunRepository class
```

## 🔬 Verify Repository Content

To see exactly what the repository has, check GitHub:

https://github.com/roeimichael/StrategyBuilder/tree/claude/add-persistent-run-storage-tSepA

Or run locally:

```cmd
python list_exports.py
```

This will show you exactly what's being exported from each module.

## ❓ Still Not Working?

### Check Git Status

```cmd
git status
```

If you see modified files that shouldn't be modified:

```cmd
git reset --hard origin/claude/add-persistent-run-storage-tSepA
```

### Check File Contents

```cmd
type src\api\models\__init__.py
```

Look for these lines:
```python
from .requests import BacktestRequest, MarketDataRequest, OptimizationRequest, ReplayRunRequest
from .responses import (
    BacktestResponse, StrategyInfo, StrategyParameters, OptimizationResponse, OptimizationResult,
    SavedRunSummaryResponse, SavedRunDetailResponse
)
```

If `ReplayRunRequest`, `SavedRunSummaryResponse`, or `SavedRunDetailResponse` are missing, you need to pull again.

### Check Exceptions Folder

```cmd
dir src\exceptions
```

You should see:
```
__init__.py
base.py
strategy_errors.py
data_errors.py
```

If these files don't exist:

```cmd
git pull origin claude/add-persistent-run-storage-tSepA --force
```

### Check if IDE is Caching

If using VSCode or PyCharm:
1. Close the IDE completely
2. Delete `.vscode` or `.idea` folders
3. Clear Python cache (Step 3 above)
4. Reopen IDE

### Recreate Virtual Environment

As a last resort:

```cmd
deactivate
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 📊 Expected Diagnostic Output

When you run `python list_exports.py`, you should see:

```
✓ BacktestRequest is exported
✓ OptimizationRequest is exported
✓ MarketDataRequest is exported
✓ ReplayRunRequest is exported        ← Must be here
✓ BacktestResponse is exported
✓ SavedRunSummaryResponse is exported  ← Must be here
✓ SavedRunDetailResponse is exported   ← Must be here
✓ StrategyNotFoundError
✓ StrategyLoadError

✅ All required models are properly exported
```

If you see anything different, your files are not in sync with the repository.

## 🎯 Bottom Line

The repository is **100% correct**. The issue is:
1. You haven't pulled the latest changes, OR
2. Python is using cached bytecode, OR
3. Your IDE is caching old file references

Follow the steps above and it will work!

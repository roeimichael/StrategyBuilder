@echo off
echo Fixing import cache issues...
echo.

echo Step 1: Pulling latest changes from git...
git pull origin claude/add-persistent-run-storage-tSepA
echo.

echo Step 2: Removing Python cache files...
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo.

echo Step 3: Verifying files exist...
if exist "src\api\models\requests.py" (
    echo [OK] src\api\models\requests.py exists
) else (
    echo [ERROR] src\api\models\requests.py NOT FOUND!
)

if exist "src\api\models\responses.py" (
    echo [OK] src\api\models\responses.py exists
) else (
    echo [ERROR] src\api\models\responses.py NOT FOUND!
)

if exist "src\api\models\__init__.py" (
    echo [OK] src\api\models\__init__.py exists
) else (
    echo [ERROR] src\api\models\__init__.py NOT FOUND!
)

if exist "src\data\run_repository.py" (
    echo [OK] src\data\run_repository.py exists
) else (
    echo [ERROR] src\data\run_repository.py NOT FOUND!
)
echo.

echo Step 4: Testing imports...
python -c "from src.api.models import ReplayRunRequest; print('[OK] ReplayRunRequest imported successfully')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Failed to import ReplayRunRequest
    echo.
    echo Trying alternative import test...
    python -c "import sys; sys.path.insert(0, '.'); from src.api.models.requests import ReplayRunRequest; print('[OK] Direct import works')"
)
echo.

echo Done! Try starting the server now:
echo   python run_api.py
echo.
pause

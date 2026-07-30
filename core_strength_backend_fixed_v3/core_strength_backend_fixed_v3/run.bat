@echo off
setlocal

REM Code Runner co the chay file voi working directory la thu muc workspace.
REM Lenh nay dam bao cac duong dan ben duoi luon tinh tu thu muc backend.
cd /d "%~dp0"

REM Tránh biến DEBUG=release của VS Code/Code Runner ghi đè cấu hình backend.
set "DEBUG="

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Chua co moi truong ao rieng cua backend:
  echo %CD%\.venv
  echo.
  echo Hay chay setup.bat truoc.
  exit /b 1
)

".venv\Scripts\python.exe" -c "import uvicorn, tzdata" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Moi truong .venv cua backend dang thieu uvicorn hoac tzdata.
  echo Dang cai dependency tu requirements.txt...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)

echo [INFO] Python: %CD%\.venv\Scripts\python.exe
echo [INFO] API: http://127.0.0.1:8000
echo [INFO] Swagger: http://127.0.0.1:8000/docs
echo.

".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
endlocal

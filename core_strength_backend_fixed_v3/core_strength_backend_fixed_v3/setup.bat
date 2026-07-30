@echo off
setlocal

REM Luon chuyen ve dung thu muc chua file setup.bat
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
  if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Khong tim thay Python trong PATH.
    echo Hay cai Python 3.11 hoac 3.12 va chon Add Python to PATH.
    exit /b 1
  )
  if not exist ".venv\Scripts\python.exe" python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Tao moi truong ao .venv that bai.
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

if not exist ".env" copy ".env.example" ".env" >nul

echo.
echo [OK] Da cai dat dependency vao:
echo %CD%\.venv
echo.
echo Hay kiem tra file .env, import database va chay run.bat.
endlocal

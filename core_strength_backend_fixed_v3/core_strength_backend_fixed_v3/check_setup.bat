@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Chua co .venv cua backend. Hay chay setup.bat.
  exit /b 1
)

".venv\Scripts\python.exe" tools\check_setup.py
endlocal

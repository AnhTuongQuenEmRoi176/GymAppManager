@echo off
setlocal
cd /d "%~dp0.."
echo [INFO] MOCK DATA
flutter run --dart-define=USE_MOCK_DATA=true
endlocal

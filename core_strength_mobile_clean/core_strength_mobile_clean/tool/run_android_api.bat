@echo off
setlocal
cd /d "%~dp0.."
echo [INFO] Android Emulator - API http://10.0.2.2:8000/api
flutter run --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://10.0.2.2:8000/api --dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
endlocal

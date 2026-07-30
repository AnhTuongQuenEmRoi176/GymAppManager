@echo off
setlocal
cd /d "%~dp0.."
echo [INFO] Chrome - API http://127.0.0.1:8000/api
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
endlocal

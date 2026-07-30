# Kết nối Flutter

Project Flutter hiện tại đã gọi đúng các endpoint sau:

| Flutter repository | Backend |
|---|---|
| Login | `POST /api/auth/login` |
| Restore session | `GET /api/auth/me` |
| Forgot password | `POST /api/auth/forgot-password` |
| Member dashboard | `GET /api/member/dashboard` |
| Trainer dashboard | `GET /api/trainer/dashboard` |
| Schedule | `GET /api/schedules?role=MEMBER` hoặc `TRAINER` |
| QR | `POST /api/qr/token` |
| Check-in history | `GET /api/checkins/history` |
| Assigned members | `GET /api/trainer/members` |
| Notifications | `GET /api/notifications` |
| Realtime | `/ws?token=<JWT>` |

Không cần sửa JSON parser của Flutter. Chỉ cần chạy với `USE_MOCK_DATA=false`.

## Android Emulator

```bat
flutter run ^
 --dart-define=USE_MOCK_DATA=false ^
 --dart-define=API_BASE_URL=http://10.0.2.2:8000/api ^
 --dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
```

## Điện thoại thật

Thay `192.168.1.20` bằng IPv4 của máy chạy backend:

```bat
flutter run ^
 --dart-define=USE_MOCK_DATA=false ^
 --dart-define=API_BASE_URL=http://192.168.1.20:8000/api ^
 --dart-define=WS_BASE_URL=ws://192.168.1.20:8000/ws
```

# CORE STRENGTH Backend

Backend riêng cho ứng dụng Flutter **CORE STRENGTH**, viết bằng **FastAPI/Python**, sử dụng chung database MySQL `gym_db` với Windows App.

## 1. Chức năng đã có

- Đăng nhập Mobile cho role `MEMBER`, `TRAINER`.
- Đăng nhập Windows API cho role `ADMIN`, `RECEPTIONIST`.
- JWT Access Token + Refresh Token và đăng xuất/thu hồi token.
- Quên mật khẩu bằng OTP; môi trường development trả `debug_otp` để kiểm thử.
- Dashboard Hội viên và Dashboard PT.
- Lịch tập/lịch dạy, tạo và cập nhật lịch.
- QR động có chữ ký, hết hạn sau 30 giây và chỉ dùng một lần.
- Quét QR đơn, quét đôi PT + Hội viên, chống ghi trùng bằng idempotency key.
- Quét đôi tự động trừ 1 buổi Hội viên, cộng KPI PT và tính hoa hồng 0,5% giá gói.
- Lịch sử check-in, gói tập, thanh toán, yêu cầu gia hạn/nâng cấp.
- Danh sách Hội viên PT phụ trách và báo cáo thu nhập PT.
- Hồ sơ, đổi mật khẩu, upload ảnh đại diện.
- Thông báo và đăng ký FCM device token.
- WebSocket realtime theo đúng từng user.
- Transactional Outbox và trigger MySQL để Windows App ghi trực tiếp DB vẫn phát realtime cho Flutter.
- Swagger API tại `/docs`.

## 2. Cấu trúc thư mục

```text
core_strength_backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   ├── router.py
│   │   └── routes/
│   ├── core/
│   ├── db/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── database/
│   ├── gym_db_full.sql
│   ├── gym_db_full_api.sql
│   └── realtime_triggers.sql
├── docs/
├── tests/
├── uploads/
├── .env.example
├── requirements.txt
├── setup.bat
└── run.bat
```

## 3. Cài đặt trên Windows

Yêu cầu:

- Python 3.11 hoặc 3.12.
- XAMPP MySQL đang chạy.
- Database tên `gym_db`.

### Bước 1: Đưa folder vào project

Có thể đặt cạnh Windows App và Flutter:

```text
GymAppManager/
├── QlyPhongGym/              # Windows App hiện tại
├── core_strength_mobile/     # Flutter
└── core_strength_backend/    # Backend này
```

### Bước 2: Import database

Nếu chưa có dữ liệu quan trọng, import file:

```text
database/gym_db_full_api.sql
```

File này chứa toàn bộ bảng, dữ liệu mẫu và trigger realtime. Nó có lệnh xóa `gym_db` cũ nên phải sao lưu trước.

Nếu đã import `gym_db_full.sql` trước đó và muốn giữ dữ liệu hiện có, chỉ import:

```text
database/realtime_triggers.sql
```

### Bước 3: Cài package

Mở terminal tại folder backend:

```bat
setup.bat
```

Sau đó mở `.env` và kiểm tra:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/gym_db?charset=utf8mb4
```

Nếu MySQL root có mật khẩu `123456`:

```env
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/gym_db?charset=utf8mb4
```

Đổi `SECRET_KEY` và `QR_SECRET_KEY` thành hai chuỗi dài, khác nhau trước khi chạy thật.

### Bước 4: Chạy backend

```bat
run.bat
```

Hoặc:

```bat
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Kiểm tra:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## 4. Chạy Flutter với API thật

`flutter run` không tự chạy backend. Cần hai terminal.

### Terminal 1

```bat
cd core_strength_backend
run.bat
```

### Terminal 2 - Android Emulator

```bat
cd core_strength_mobile
flutter run ^--dart-define=USE_MOCK_DATA=false ^--dart-define=API_BASE_URL=http://10.0.2.2:8000/api ^--dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
```

### Điện thoại thật

Điện thoại và máy tính phải chung Wi-Fi. Lấy IPv4 máy tính bằng `ipconfig`, ví dụ `192.168.1.20`:

```bat
flutter run ^
  --dart-define=USE_MOCK_DATA=false ^
  --dart-define=API_BASE_URL=http://192.168.1.20:8000/api ^
  --dart-define=WS_BASE_URL=ws://192.168.1.20:8000/ws
```

Cho phép Python/Uvicorn qua Windows Firewall nếu điện thoại không kết nối được.

## 5. Tài khoản mẫu

| Ứng dụng | Username | Mật khẩu |
|---|---|---|
| Flutter Hội viên | `member` | `123456` |
| Flutter PT | `trainer` | `123456` |
| Windows Admin API | `admin` | `admin123` |
| Windows Lễ tân API | `receptionist` | `123456` |

## 6. Realtime với Windows App hiện tại

Windows App hiện có thể tiếp tục ghi trực tiếp MySQL. Các trigger trong `realtime_triggers.sql` sẽ ghi sự kiện vào `outbox_events`. Backend đọc bảng này mỗi giây và gửi WebSocket đến đúng Hội viên/PT đang đăng nhập Flutter.

Các sự kiện Flutter đã hỗ trợ:

```text
checkin.confirmed
schedule.created
schedule.updated
schedule.cancelled
membership.updated
membership.sessions_changed
pt_session.created
trainer.kpi_changed
notification.created
```

Để nghiệp vụ quét đôi luôn đúng và chạy trong một transaction, Windows App nên gọi:

```text
POST /api/checkins/scan
POST /api/checkins/confirm
POST /api/checkins/confirm-pair
```

Chi tiết xem `docs/WINDOWS_INTEGRATION.md`.

## 7. Lưu ý quên mật khẩu

Backend đã có logic tạo, kiểm tra và hết hạn OTP. Chưa cấu hình dịch vụ gửi email/SMS vì tài liệu và database hiện tại không có thông tin nhà cung cấp.

- Khi `DEBUG=true`, endpoint trả thêm `debug_otp` để kiểm thử.
- Khi triển khai thật, đặt `DEBUG=false` và tích hợp SMTP, SendGrid, Twilio hoặc nhà cung cấp SMS Việt Nam.

## 8. Kiểm thử

```bat
.venv\Scripts\activate
pytest
```

## 9. Điểm cần giữ thống nhất

- Không cho Flutter kết nối trực tiếp MySQL.
- Tất cả thời gian database dùng timezone `Asia/Ho_Chi_Minh`.
- QR không chứa ID thuần; token được ký và lưu hash trong database.
- Access Token đưa trong header `Authorization: Bearer <token>`.
- WebSocket kết nối bằng `ws://SERVER:8000/ws?token=<access_token>`.

## Sửa lỗi múi giờ trên Windows

Python trên Windows thường không có sẵn IANA time-zone database. Dự án đã thêm `tzdata` vào `requirements.txt`. Nếu gặp lỗi `ZoneInfoNotFoundError`, chạy:

```bat
.venv\Scripts\python.exe -m pip install tzdata
```

Sau đó chạy lại `run.bat`.


## Lỗi `debug = release` trên Windows / VS Code

Backend dùng biến `APP_DEBUG=true|false`, không dùng biến chung `DEBUG`.
Nếu file `.env` cũ có dòng `DEBUG=...`, có thể xóa dòng đó hoặc đổi thành:

```env
APP_DEBUG=true
```

# CORE STRENGTH Mobile – Clean UI

Ứng dụng Flutter dành cho **Hội viên** và **Huấn luyện viên cá nhân**, kết nối backend FastAPI qua REST API và WebSocket realtime.

## Những phần đã hoàn thiện lại

- Làm lại toàn bộ màu sắc, card, panel, khoảng cách và kích thước chữ theo cùng một design system.
- Giao diện responsive, khi chạy Chrome/Windows được căn giữa với chiều rộng mobile tối đa 520px.
- Trang đăng nhập không còn tự điền `member / 123456`.
- Không hiển thị URL API trên giao diện đăng nhập.
- Lỗi API hiển thị rõ nhưng cùng tone với giao diện.
- Quên mật khẩu có đủ luồng: tài khoản → OTP → mật khẩu mới → nhập lại mật khẩu.
- Đổi mật khẩu có ba trường: mật khẩu hiện tại, mật khẩu mới và nhập lại mật khẩu mới.
- Đổi mật khẩu gọi thật endpoint `POST /api/auth/change-password`.
- Làm lại dashboard Hội viên, dashboard PT, QR check-in, lịch tập, lịch sử, thông báo, danh sách hội viên và hồ sơ.
- Loại bỏ các nút hoặc mục chỉ để minh họa nhưng chưa có logic thật.
- Dio đã hỗ trợ `DioExceptionType.transformTimeout` và ẩn mật khẩu/token khỏi log.

## Cấu trúc chính

```text
lib/
├── app/
├── core/
│   ├── config/
│   ├── network/
│   ├── realtime/
│   ├── storage/
│   ├── theme/
│   └── widgets/
└── features/
    ├── auth/
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    └── gym/
        ├── data/
        ├── domain/
        └── presentation/
```

## Tạo platform Flutter lần đầu

Project source không kèm thư mục platform nặng. Chạy:

```bat
tool\setup_project.bat
```

Hoặc chạy thủ công:

```bat
flutter create --project-name core_strength_mobile --org com.corestrength --platforms android,ios,web .
flutter pub get
```

## Chạy với backend thật

Backend FastAPI phải chạy trước tại cổng `8000`.

### Chrome

```bat
tool\run_chrome_api.bat
```

Tương đương:

```bat
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

### Windows

```bat
tool\run_windows_api.bat
```

### Android Emulator

```bat
tool\run_android_api.bat
```

Android Emulator dùng `10.0.2.2` để truy cập backend trên máy tính.

### Điện thoại thật

Thay `192.168.1.20` bằng IPv4 của máy tính:

```bat
flutter run --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://192.168.1.20:8000/api --dart-define=WS_BASE_URL=ws://192.168.1.20:8000/ws
```

## Chạy mock để xem giao diện

```bat
tool\run_mock.bat
```

Tài khoản mock chỉ dùng khi chạy `USE_MOCK_DATA=true`:

```text
Hội viên: member / 123456
PT: trainer / 123456
```

Các trường đăng nhập luôn để trống khi mở ứng dụng.

## Endpoint xác thực được sử dụng

```text
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/forgot-password
POST /api/auth/reset-password
POST /api/auth/change-password
```

## Kiểm tra trước khi chạy

```bat
flutter clean
flutter pub get
flutter analyze
```

Sau đó mới chạy Chrome, Windows hoặc Android.

# Validation Report

Đã kiểm tra tự động trong môi trường tạo source:

- 52 file Dart.
- Không có import tương đối bị thiếu.
- Không có ngoặc `()`, `[]`, `{}` bị lệch theo kiểm tra tĩnh.
- Không còn `const ListView(...)` gây lỗi constructor.
- Không còn controller đăng nhập khởi tạo sẵn `member` hoặc `123456`.
- Dio switch đã có `DioExceptionType.transformTimeout`.
- Tất cả implementation của `AuthRepository` có đủ:
  - requestPasswordReset
  - resetPassword
  - changePassword
- Mật khẩu và refresh token được che khỏi log request.

Môi trường tạo source không cài Flutter SDK nên chưa chạy trực tiếp được:

```text
flutter analyze
flutter run
```

Sau khi giải nén trên máy phát triển, chạy:

```bat
flutter clean
flutter pub get
flutter analyze
```

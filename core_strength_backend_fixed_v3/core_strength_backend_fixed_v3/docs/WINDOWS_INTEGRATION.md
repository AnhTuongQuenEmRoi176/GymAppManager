# Tích hợp Windows App

## Phương án chạy ngay, ít sửa Windows App

1. Windows App tiếp tục dùng SQLAlchemy/PyMySQL và ghi trực tiếp `gym_db`.
2. Import `database/realtime_triggers.sql`.
3. Backend đọc `outbox_events` và gửi WebSocket cho Flutter.

Phương án này đảm bảo thay đổi lịch, số buổi, check-in, KPI và thông báo được tải lại realtime trên Flutter.

## Phương án khuyến nghị cho chức năng QR

Đăng nhập lễ tân:

```http
POST /api/windows/auth/login
Content-Type: application/json

{
  "username": "receptionist",
  "password": "123456",
  "device_name": "WINDOWS-CAM-01"
}
```

Quét và xem thông tin QR, chưa ghi check-in:

```http
POST /api/checkins/scan
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "token": "<qr_token_từ_flutter>"
}
```

Xác nhận QR đơn:

```http
POST /api/checkins/confirm
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "token": "<qr_token>",
  "location": "Quầy check-in chính",
  "device_id": "WINDOWS-CAM-01",
  "idempotency_key": "camera-01-20260730-00001",
  "manual_override": false
}
```

Xác nhận quét đôi PT + Hội viên:

```http
POST /api/checkins/confirm-pair
Authorization: Bearer <staff_access_token>
Content-Type: application/json

{
  "member_token": "<member_qr_token>",
  "trainer_token": "<trainer_qr_token>",
  "location": "Quầy check-in chính",
  "device_id": "WINDOWS-CAM-01",
  "idempotency_key": "camera-01-pair-20260730-00001",
  "manual_override": false
}
```

Endpoint quét đôi xử lý trong một transaction:

- Xác thực hai token.
- Chống sử dụng token lần hai.
- Kiểm tra gói còn hạn và số buổi còn lại.
- Kiểm tra PT có khớp PT phụ trách.
- Ghi hai check-in.
- Trừ một buổi Hội viên.
- Tạo `pt_sessions` và cộng KPI PT.
- Tính hoa hồng bằng `giá gói × 0,5%`.
- Đánh dấu lịch gần nhất hoàn thành nếu phù hợp.
- Tạo thông báo cho Hội viên và PT.

`manual_override=true` chỉ nên cho Admin/Lễ tân sử dụng sau khi kiểm tra thủ công.

# Ghi chú tích hợp với Windows App hiện tại

## Phần database hiện tại dùng được

- `users`: thông tin đăng nhập, tên, số điện thoại, email, avatar.
- `trainers`: hồ sơ PT, chuyên môn, ngày làm việc, lương cứng.
- `members`: hồ sơ hội viên và trạng thái.
- `packages`: tên gói, giá, thời hạn, số buổi.
- `member_packages`: gói hội viên đang dùng, ngày hết hạn, PT và số buổi còn lại.
- `checkins`: lịch sử quét mã.
- `pt_sessions`: buổi PT đã xác nhận.
- `transactions`: dữ liệu thanh toán/lương cơ bản.

## Phần chưa đủ dữ liệu

### 1. Lịch tập/lịch dạy tương lai

`pt_sessions` chỉ phù hợp lưu buổi đã phát sinh/xác nhận, chưa đủ để lưu lịch hẹn tương lai, giờ kết thúc, trạng thái hủy và ghi chú.

**Bổ sung:** bảng `training_schedules`.

### 2. QR động dùng một lần

`qr_demo` chỉ phù hợp mã demo tĩnh. Mobile cần token hết hạn nhanh, trạng thái đã dùng và liên kết người dùng.

**Bổ sung:** bảng `qr_tokens`.

### 3. Thông báo mobile

Schema cũ chưa có thông báo và token thiết bị.

**Bổ sung:** `notifications`, `device_tokens`.

### 4. Refresh token

Schema cũ chưa có cơ chế thu hồi phiên đăng nhập.

**Bổ sung:** `refresh_tokens`.

### 5. Role mobile

Tài liệu Windows App chỉ nêu Admin và Lễ tân. Flutter cần thêm role `MEMBER` và `TRAINER` trong bảng `roles`. Tài khoản PT/hội viên phải liên kết với `trainers.user_id` hoặc `members.user_id`.

## Bắt buộc để realtime hoạt động đúng

Không để Windows App vừa ghi trực tiếp MySQL vừa mong backend tự biết ngay để phát WebSocket. Có hai phương án:

1. **Khuyến nghị:** Windows App gọi API cho các nghiệp vụ tạo/sửa/check-in. API ghi database và phát realtime.
2. **Tạm thời:** Windows App vẫn ghi MySQL, sau đó gọi endpoint `/events/publish` để backend phát sự kiện. Phương án này dễ lệch dữ liệu nếu thao tác DB thành công nhưng gọi publish thất bại.

## Mapping QR đôi PT + Hội viên

Khi lễ tân xác nhận một cặp QR, backend cần chạy trong một transaction:

1. Khóa `member_packages` hiện hành.
2. Kiểm tra gói còn hạn và `sessions_remaining > 0`.
3. Tạo check-in PT.
4. Tạo check-in hội viên.
5. Tạo `pt_sessions`.
6. Trừ một buổi trong `member_packages.sessions_remaining`.
7. Đánh dấu cả hai QR đã dùng.
8. Commit.
9. Phát sự kiện WebSocket cho PT và hội viên.

# Clean UI Changelog

## Design system

- Primary: `#2027A8`
- Primary dark: `#151A78`
- Background: `#F6F7FB`
- Surface: `#FFFFFF`
- Border: `#E4E6EF`
- Success: `#2FA653`
- Warning: `#E58A17`
- Error: `#E5484D`

Quy chuẩn:

- Lề ngang: 16px
- Khoảng cách section: 20px
- Khoảng cách card: 12px
- Card radius: 16px
- Input/button radius: 13px
- Body: 14px
- Caption: 12px
- Page title: 22px

## Logic đã sửa

1. Xóa dữ liệu khởi tạo `member` và `123456` trong controller đăng nhập.
2. Xóa phần URL API khỏi giao diện người dùng.
3. Quên mật khẩu có OTP, mật khẩu mới và xác nhận mật khẩu mới.
4. Đổi mật khẩu bắt buộc nhập lại mật khẩu mới.
5. Mật khẩu mới phải khác mật khẩu hiện tại.
6. Loại bỏ các menu “sắp có” không có API thật.
7. Bộ lọc lịch theo tuần dùng đúng thứ Hai đến Chủ nhật.
8. Bộ lọc lịch sử theo ngày có thể xóa và thực sự lọc dữ liệu.
9. Nút tăng độ sáng giả trên QR đã bị loại bỏ.
10. Các lỗi API, cảnh báo và trạng thái dùng một component thống nhất.

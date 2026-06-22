
# Báo cáo tiến độ dự án Qly Phong Gym

## Ngày cập nhật: 2026-06-21

### 1. Mục tiêu chung
- Cập nhật app quản lý phòng gym theo yêu cầu từ `Prompt_CodeGeeX_GymApp.docx`.
- Hoàn thiện giao diện PyQt6 desktop, backend MySQL/SQLAlchemy, quét QR camera, vai trò Admin/Receptionist, quản lý gói/PT/hội viên/báo cáo.

### 2. Đã làm xong
- `app/ui/package_registration.py`
  - Hoàn thiện bước đăng ký gói:
    - chọn gói → chọn hội viên → chọn PT tùy chọn → xác nhận
    - tính phí PT theo số buổi
    - tổng tiền hiển thị rõ ràng
  - Sửa lỗi nút chọn PT, reset lựa chọn đúng khi bỏ PT
  - Thêm bản xem trước thanh toán

- `app/ui/tab_dashboard.py`
  - Sửa lỗi xử lý và ghi ảnh checkin
  - Giữ lại luồng xác nhận cho cả hội viên và PT
  - Cải thiện hiển thị thông tin đối tượng khi quét QR
  - Hỗ trợ `Thủ công` và `Tự động`

- `app/ui/tab_trainers.py`
  - Chuyển từ danh sách đơn giản sang giao diện thẻ PT
  - Thêm tìm kiếm PT
  - Hiển thị số buổi đã dạy và gói PT đang quản lý
  - Thêm nút `Chi tiết`, `Sửa`, `Xóa` trên mỗi thẻ

- `app/ui/trainer_detail.py`
  - Mở rộng chi tiết PT
  - Hiển thị tên hội viên và người xác nhận khi có buổi PT

- `app/ui/tab_reports.py`
  - Giữ lại tính năng báo cáo doanh thu, lọc theo ngày và loại giao dịch
  - Cải thiện biểu đồ và tính toán lãi/lỗ
  - Thêm summary doanh thu: `Doanh thu`, `Lương PT`, `Lãi/Lỗ`
  - Thêm bảng tổng hợp doanh thu theo PT và thông báo lưu Excel

- `app/ui/tab_dashboard.py`
  - Hoàn thiện xác nhận `member + trainer` ở chế độ thủ công
  - Gán `scanner_user_id` cho mọi checkin

- `app/ui/tab_trainers.py`
  - Hiển thị trạng thái PT (Hoạt động/Ngưng) và lương cơ bản
  - Duy trì giao diện thẻ PT và tìm kiếm

### 3. Còn cần hoàn thiện
- Kiểm thử giao diện mới `TabTrainers` với dữ liệu thật
- Làm đẹp stylesheet chung để thẻ PT và tab thống kê thống nhất
- Kiểm tra kỹ flow `dashboard` khi quét đồng thời hội viên + PT
- Hoàn thiện báo cáo `PT salary` và `profit/loss` thực tế theo chuẩn nghiệp vụ

### 4. Gợi ý cho AI tiếp theo
- Kiểm tra database schema `app/models.py` để bổ sung `salary`/`commission` cho PT nếu cần
- Thêm validate role `Admin`/`Receptionist` cho các tab liên quan
- Hoàn thiện `tab_reports.py` với báo cáo chi tiết doanh thu gói, doanh thu PT, chi phí lương
- Chuẩn hóa UI theo theme tối/light của app

### 5. Tệp đã chỉnh sửa chính
- `app/ui/package_registration.py`
- `app/ui/tab_dashboard.py`
- `app/ui/tab_trainers.py`
- `app/ui/trainer_detail.py`
- `app/ui/tab_reports.py`

---

## Ghi chú kỹ thuật
- Cần test lại camera/OpenCV trên môi trường Windows để tránh lỗi `QImage`/`QPixmap` khi đọc ảnh
- Nên dùng `session.query(...).count()` thận trọng vì có thể chậm trên bảng lớn; cân nhắc load số liệu tổng hợp riêng nếu cần
- `MemberPackage.end_date >= date.today()` dùng để xác định gói PT hiện tại


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

---

## Cập nhật 2026-06-23 - Tối ưu hiệu năng và giao diện

### Đã làm
- `app/main.py`
  - Chuyển MainWindow sang lazy-load tab: app chỉ tạo tab khi người dùng mở tab đó.
  - Loại import trực tiếp toàn bộ tab lúc khởi động để giảm thời gian mở app và RAM ban đầu.
  - Thêm nút chuyển chế độ sáng/tối ở sidebar, dùng `apply_app_theme()`.

- `app/ui/theme.py`
  - Tách bảng màu dark/light và thêm `build_stylesheet(mode)`, `apply_app_theme(app, mode)`.
  - Bỏ nền/box sau `QLabel` thường để text không bị lệch với button/panel.
  - Làm chữ title/section/stat rõ hơn.
  - Thêm màu button theo vai trò: primary, secondary, success, warning, danger, ghost.
  - Giữ `configure_table()` khóa edit trực tiếp trong bảng, tránh sửa nhầm ô.

- `app/ui/tab_dashboard.py`
  - Lazy import `CameraWorker` khi bấm Bật camera, không nạp camera/OpenCV lúc mở app.
  - Lazy import `cv2` khi cần lưu ảnh check-in.
  - Sửa chế độ QR tự động bị quét liên tục gây lag:
    - thêm `pending_entities`, `confirming`, `auto_pause_until` để không xác nhận chồng nhau;
    - tăng cooldown auto scan;
    - auto check-in không bật QMessageBox liên tục;
    - không xóa debounce ngay sau auto confirm.

- `app/utils/camera_worker.py`
  - Lazy import `cv2` và `decode_qr_from_frame` bên trong `run()`.
  - Giảm FPS mặc định xuống 10.
  - Chỉ decode QR mỗi vài frame (`decode_every=3`) để giảm tải CPU.

- `app/ui/tab_reports.py`
  - Lazy import `matplotlib`, `pyqtgraph` chỉ khi bấm Xem báo cáo.
  - Lazy import `pandas` chỉ khi bấm Xuất Excel.
  - Nút Xuất Excel dùng màu secondary.

- Các tab/form UI
  - Tô màu nút theo chức năng ở các màn chính: tìm/xuất/chi tiết = secondary, sửa = warning, xóa = danger, bật camera/thêm gói = success, hủy = ghost.

### Kiểm tra đã chạy
- Kiểm tra syntax trực tiếp bằng `compile()` cho toàn bộ `app/ui/*.py`, `app/main.py`, `app/utils/camera_worker.py`.
- Kiểm tra import: `app.main`, `app.ui.tab_dashboard`, `app.ui.tab_reports` import OK.
- Xác nhận sau import app chính chưa nạp các thư viện nặng: `cv2=False`, `pandas=False`, `matplotlib=False`.

### Ghi chú cho AI tiếp theo
- Project đang nằm ở `D:\GymAppManager\QlyPhongGym` trong phiên này, không phải `D:\QlyPhongGym`.
- Nếu test bằng `python -m compileall app` gặp PermissionError ở `__pycache__`, dùng `python -B` hoặc kiểm tra syntax bằng `compile()` để tránh ghi `.pyc`.
- Cần test thủ công camera thật để xác nhận cooldown auto scan phù hợp thực tế.
- Có thể tiếp tục làm đẹp sâu hơn bằng cách thêm icon vào button, nhưng hiện chưa thêm dependency icon để giữ app nhẹ.

---

## Cập nhật 2026-06-23 - Check-in chi tiết, validate form, tài khoản mặc định

### Đã làm
- `app/ui/validators.py`
  - Thêm helper validate dùng chung: bắt buộc, SĐT, email, ngày ISO `YYYY-MM-DD`, số tiền.

- `app/ui/member_form.py`
  - Thêm trường Email.
  - Validate họ tên, SĐT, email, ngày sinh.
  - Khi tạo hội viên mới: username = SĐT, mật khẩu mặc định = `12345678`.
  - Kiểm tra trùng username/SĐT trước khi tạo hoặc sửa.
  - Hiển thị ngày thêm từ `users.created_at`; người thêm hiện chưa lưu được vì schema chưa có cột `created_by` cho user/member.

- `app/ui/trainer_form.py`
  - Thêm trường Email.
  - Validate họ tên, SĐT, email, bộ môn, ngày vào, lương cứng.
  - Khi tạo PT mới: username = SĐT, mật khẩu mặc định = `12345678`.
  - Kiểm tra trùng username/SĐT trước khi tạo hoặc sửa.
  - Hiển thị ngày thêm từ `users.created_at`; người thêm hiện chưa lưu được vì schema chưa có cột `created_by` cho user/trainer.

- `app/ui/package_form.py`
  - Validate tên gói, giá, thời hạn, số buổi.

- `app/ui/receptionist_form.py`
  - Validate username, họ tên, SĐT, mật khẩu tối thiểu 8 ký tự khi tạo mới/đổi mật khẩu.
  - Kiểm tra trùng username/SĐT.

- `app/ui/tab_members.py`
  - Bảng hội viên thêm cột Email và Ngày thêm.

- `app/ui/tab_trainers.py`
  - Card PT hiển thị thêm Email và Ngày thêm.

- `app/ui/checkin_detail.py`
  - Double click lịch sử check-in mở dialog chi tiết có scroll.
  - Nếu là buổi tập PT, tự tìm bản ghi đối ứng cùng ảnh/thời điểm để hiển thị cả hội viên và PT.
  - Hiển thị avatar từng người và ảnh snapshot khi quét.
  - Hiển thị lễ tân quét, nguồn, QR payload.

- `app/ui/tab_dashboard.py`
  - Chế độ tự động sau khi lưu check-in vẫn giữ ảnh và thông tin người vừa quét ở panel bên phải, chỉ đổi trạng thái thành đã tự động lưu.

- `app/ui/tab_reports.py`
  - Bọc màn báo cáo doanh thu bằng `QScrollArea`.
  - Tăng chiều cao vùng biểu đồ để tránh bảng/biểu đồ đè nhau trên màn hình thấp.

### Kiểm tra đã chạy
- Syntax toàn bộ `app/ui/*.py`, `app/main.py`, `app/utils/camera_worker.py` OK bằng `python -B` + `compile()`.
- Import `app.main`, `member_form`, `trainer_form`, `checkin_detail`, `tab_reports` OK.
- Sau import vẫn chưa nạp thư viện nặng: `cv2=False`, `pandas=False`, `matplotlib=False`.

### Còn nên làm nếu muốn quản lý người thêm thật sự
- Cần migration DB thêm cột `created_by` cho `users` hoặc riêng `members/trainers/packages`.
- Sau đó cập nhật model SQLAlchemy và form tạo mới để lưu `get_current_user().id`.

## 2026-06-23 - Tối ưu nhẹ app, validate đăng ký, QR clear, reload/date picker

### Đã làm
- `requirements.txt`
  - Gỡ phụ thuộc trực tiếp nặng/không còn cần: `matplotlib`, `Pillow`, `opencv-python`.
  - Đổi sang `opencv-python-headless` để nhẹ hơn khi chạy app PyQt, giữ `qrcode[pil]` để QR vẫn có backend ảnh.
  - Giữ `pandas/openpyxl` vì chức năng xuất Excel của báo cáo vẫn dùng khi người dùng bấm xuất file.

- `app/ui/tab_reports.py`
  - Bỏ toàn bộ render chart bằng `matplotlib`; chuyển biểu đồ sang `pyqtgraph` để giảm tải import và dung lượng đóng gói.
  - Bộ lọc ngày dùng format `dd/MM/yyyy`, có nút nhanh `Hôm nay`, `30 ngày`, và nút reload `↻`.
  - Import app chính không còn kéo `matplotlib`, `pandas`, `cv2` vào ngay từ đầu.

- `app/ui/login.py`
  - Đổi brand/login window sang `Apex Gym`.
  - Form đăng ký lễ tân validate SĐT, bắt buộc họ tên/tên đăng nhập, mật khẩu tối thiểu 8 ký tự.
  - Thêm ô nhập lại mật khẩu và kiểm tra khớp mật khẩu.
  - Kiểm tra trùng SĐT khi đăng ký.

- `app/main.py`, `app/ui/theme.py`
  - Đổi tên app/window title thành `Apex Gym - Quản lý phòng gym`.
  - Sidebar brand thành `Apex Gym`.
  - Thêm top bar nội bộ cho app chính và style cho nút icon reload.
  - Lưu ý: title bar gốc của Windows chưa custom frameless để tránh tăng rủi ro lỗi resize/drag window.

- `app/ui/member_form.py`, `app/ui/trainer_form.py`
  - Ngày sinh hội viên và ngày vào của PT chuyển sang `QDateEdit` có calendar popup, format `dd/MM/yyyy`.

- `app/ui/tab_dashboard.py`
  - Form check-in có thêm nút `Từ chối` khi QR đã được nhận diện.
  - Nếu lễ tân không xác nhận/từ chối trong 5 giây thì tự clear thông tin QR.
  - Sau khi xác nhận/auto check-in, panel giữ trạng thái ngắn rồi clear sau 5 giây, tránh quét lặp gây lag.

- Các tab chính
  - Thêm nút reload `↻` cho: Lịch sử check-in, Hội viên, PT, Gói tập, Lễ tân, QR demo, Báo cáo.
  - Lịch sử check-in có quick filter `Hôm nay` và `7 ngày`, date picker format `dd/MM/yyyy`.

### Kiểm tra đã chạy
- Syntax toàn bộ `app/ui/*.py`, `app/main.py`, `app/utils/camera_worker.py` OK bằng `python -B` + `compile()`.
- Import `app.main` OK.
- Sau import app chính: `cv2=False`, `pandas=False`, `matplotlib=False`.

### Lưu ý cho lần sau
- Nếu camera gặp lỗi với `opencv-python-headless` trên máy Windows cụ thể, cân nhắc đổi lại `opencv-python`. Hiện code vẫn lazy import `cv2`, nên chỉ ảnh hưởng lúc bật camera.
- Muốn custom title bar Windows thật sự đẹp hơn nữa thì nên làm frameless window riêng, nhưng cần xử lý kéo cửa sổ, resize, minimize/maximize/close cẩn thận.

### Hotfix 2026-06-23 - Sửa crash reload/quick filter
- Sửa `app/ui/tab_history.py`: khởi tạo đúng `btn_today`, `btn_7days`, `btn_reload` trước khi add vào layout; sửa label bị lỗi encoding; làm `__del__` an toàn khi Qt đã hủy `QTimer`.
- Sửa `app/ui/tab_members.py`, `app/ui/tab_trainers.py`, `app/ui/tab_qrdemo.py`, `app/ui/tab_receptionists.py`: đảm bảo `btn_reload` được tạo trước khi dùng và đã connect về hàm refresh/reload tương ứng.
- Đã test runtime bằng `QT_QPA_PLATFORM=offscreen`: `TabHistory`, `TabMembers`, `TabTrainers`, `TabQRDemo`, `TabReceptionists` khởi tạo OK.

### 2026-06-23 - Admin delete guard, thôi việc, tổng hợp lương PT
- Thêm `app/payroll.py` với công thức dùng chung: `lương = lương cứng + số buổi PT * hệ số/buổi`; hệ số mặc định hiện là `50000`.
- Thêm tab admin `Lương` (`app/ui/tab_payroll.py`): lọc kỳ lương, chỉnh hệ số/buổi, xem tổng lương PT và ghi nhận thanh toán lương bằng `transactions.type = salary`.
- `app/main.py`: thêm tab `Lương`, chỉ admin được truy cập.
- `app/ui/trainer_detail.py`: hiển thị thêm hệ số/buổi và thu nhập tạm tính cho PT.
- `app/ui/tab_trainers.py`: thêm nút `Cho nghỉ` cho PT; chỉ admin được cho nghỉ/xóa. Cho nghỉ sẽ set `trainers.end_date = today` và `users.is_active = False` để giữ lịch sử.
- `app/ui/tab_receptionists.py`: thêm trạng thái, nút `Cho nghỉ`; chỉ admin được cho nghỉ/xóa. Cho nghỉ sẽ set `users.is_active = False`.
- `app/ui/login.py`: chặn đăng nhập với tài khoản `is_active = False`.
- Logic xóa đã đổi sang admin-only và chặn xóa khi còn ràng buộc:
  - Hội viên: chặn nếu có gói tập, check-in, buổi PT, QR demo.
  - PT: chặn nếu còn/đã quản lý gói PT, có buổi PT, check-in, QR demo.
  - Gói tập: chặn nếu đã từng được đăng ký.
  - Lễ tân: chặn nếu đã quét check-in, xác nhận buổi PT hoặc tạo giao dịch.
- Lọc PT đã nghỉ khỏi màn đăng ký gói và QR demo để tránh giao việc mới cho người đã thôi việc.

### Kiểm tra đã chạy
- Compile toàn bộ `app/**/*.py` OK.
- Runtime offscreen OK cho `TabTrainers`, `TabMembers`, `TabPackages`, `TabReceptionists`, `TabPayroll`.
- Rà các label mới trong `tab_trainers.py`, `tab_history.py`, `tab_receptionists.py`, `tab_payroll.py`: không còn ký tự `?` nghi do lỗi Unicode.

### 2026-06-23 - Mở rộng lương PT/nhân viên và nối lãi lỗ
- `app/ui/trainer_detail.py`: chi tiết PT hiển thị thu nhập tháng hiện tại gồm: số buổi tháng này, hệ số/buổi, tiền theo buổi, lương cứng, tổng thu nhập tháng; bảng bên dưới chỉ liệt kê các buổi PT trong tháng hiện tại và tiền/buổi.
- `app/ui/tab_payroll.py`: viết lại tab Lương cho tất cả nhân viên:
  - Gồm PT và lễ tân.
  - Lọc theo ngày/tháng, nút `Tháng này`, tìm kiếm theo tên/SĐT/vai trò.
  - Sort theo tên, tổng lương cao, còn phải trả cao, số buổi PT cao, vai trò.
  - Có hệ số/buổi PT và lương lễ tân/kỳ để admin chỉnh khi tính.
  - Tính tổng lương, đã thanh toán, còn phải trả.
  - Thanh toán lương ghi `transactions.type = salary` kèm token `payroll:{type}:{id}` để lần sau nhận biết đã trả.
  - Xuất Excel bảng lương hiện tại.
- `app/payroll.py`: thêm `DEFAULT_RECEPTIONIST_SALARY` và `salary_token()`.
- `app/ui/tab_reports.py`: lãi/lỗ nay trừ chi phí lương theo kỳ. Chi phí lương = max(lương đã thanh toán, lương dự kiến theo buổi PT + lương lễ tân mặc định). Đổi thẻ báo cáo thành `Chi phí lương` và thêm các dòng tóm tắt lương đã thanh toán/lương dự kiến/chi phí lương tính lãi lỗ.

### Kiểm tra đã chạy
- Compile toàn bộ `app/**/*.py` OK.
- Runtime offscreen OK cho `TabPayroll`, `TabReports`.

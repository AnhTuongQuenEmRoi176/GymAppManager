# Bản vá chức năng lên lịch – GymAppManager

Bản này **chỉ bổ sung phần lịch**, không thay toàn bộ Windows App, Flutter hay backend.

## Chức năng được thêm

### Windows App – Admin/Lễ tân

- Thêm tab **Lịch tập & lịch dạy** vào sidebar hiện tại.
- Xem lịch theo khoảng ngày và trạng thái.
- Tìm theo tên/SĐT PT, hội viên hoặc nội dung buổi tập.
- Thêm, sửa, hủy lịch.
- Chỉ hiện hội viên đang có gói PT của PT được chọn.
- Chặn trùng lịch của cả PT và hội viên.

### Flutter – PT

- Nút **Tạo lịch** tại màn Lịch dạy.
- Chọn hội viên đang được PT phụ trách.
- Nhập nội dung, ngày giờ, địa điểm và ghi chú.
- Sửa hoặc hủy lịch chưa kết thúc.
- Không cho tạo lịch quá khứ.
- Hiển thị lỗi trùng lịch do backend trả về.

Hội viên vẫn chỉ xem lịch. Khi PT tạo/sửa/hủy, hội viên nhận cập nhật realtime nếu database đã có `outbox_events` và trigger lịch.

### Backend FastAPI

- PT không cần truyền `trainer_id`; backend tự lấy PT từ JWT.
- API danh sách hội viên trả thêm `member_package_id`.
- Kiểm tra hội viên đúng PT, gói còn hiệu lực, còn số buổi.
- Chặn trùng giờ của PT và hội viên khi tạo hoặc sửa.

---

# 1. Áp dụng cho Windows App

Copy các file trong:

```text
windows_app/QlyPhongGym/
```

vào đúng thư mục `QlyPhongGym` hiện tại. Các file mới gồm:

```text
app/ui/tab_schedules.py
app/ui/schedule_form.py
apply_windows_schedule_patch.py
migrations/add_training_schedules.sql
migrations/add_schedule_realtime_triggers.sql
```

Mở terminal tại thư mục `QlyPhongGym` rồi chạy:

```bat
python apply_windows_schedule_patch.py
```

Script chỉ thực hiện hai thay đổi nhỏ:

1. Thêm model `TrainingSchedule` vào cuối `app/models.py` trước `Transaction`.
2. Thêm một dòng menu lịch vào danh sách `pages` trong `app/main.py`.

Script tự tạo file sao lưu:

```text
app/models.py.schedule_backup
app/main.py.schedule_backup
```

## Database

Nếu đang dùng file `gym_db_full_api.sql` thì bảng lịch đã có, **không cần** chạy lại `add_training_schedules.sql`.

Nếu database vẫn là schema Windows App cũ, import:

```text
migrations/add_training_schedules.sql
```

Nếu database đã có bảng `outbox_events`, import thêm:

```text
migrations/add_schedule_realtime_triggers.sql
```

Trigger này giúp lịch tạo trực tiếp trong Windows App cập nhật sang Flutter qua WebSocket.

---

# 2. Áp dụng cho backend

Copy đè đúng ba file trong:

```text
backend/core_strength_backend/
```

vào backend hiện tại:

```text
app/api/routes/schedules.py
app/api/routes/trainers.py
app/schemas/schedule.py
```

Sau đó dừng và chạy lại backend:

```bat
run.bat
```

Swagger kiểm tra:

```text
http://127.0.0.1:8000/docs
```

Các API liên quan:

```text
GET   /api/trainer/members
GET   /api/schedules
POST  /api/schedules
PATCH /api/schedules/{schedule_id}
```

---

# 3. Áp dụng cho Flutter

Copy đè thư mục:

```text
flutter/core_strength_mobile/lib/
```

vào `lib/` của Flutter hiện tại. Bản vá chỉ thay các file liên quan repository, API và lịch; đồng thời thêm:

```text
lib/features/gym/presentation/pages/schedule_form_page.dart
```

Chạy lại:

```bat
flutter clean
flutter pub get
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

## Luồng kiểm tra

1. Đăng nhập Flutter bằng tài khoản PT.
2. Mở **Lịch dạy**.
3. Bấm **Tạo lịch**.
4. Chọn hội viên đang phụ trách.
5. Chọn ngày giờ tương lai và lưu.
6. Mở Windows App → **Lịch tập & lịch dạy** để thấy cùng bản ghi.
7. Đăng nhập mobile hội viên để kiểm tra lịch vừa tạo.

## Điều kiện để danh sách hội viên của PT có dữ liệu

Bảng `member_packages` phải có bản ghi:

- `pt_id` đúng PT đang đăng nhập.
- `status = active` ở database API.
- Ngày hiện tại nằm trong `start_date` và `end_date`.
- `sessions_remaining > 0` hoặc không giới hạn.

flutter run -d edge --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
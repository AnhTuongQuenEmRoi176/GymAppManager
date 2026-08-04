# HƯỚNG DẪN TOÀN BỘ PROJECT GYM APP MANAGER

## 1. Tổng quan hệ thống

Project gồm 4 phần chạy độc lập nhưng dùng chung một database MySQL:

```text
Windows App PyQt6 (Admin/Lễ tân)
            │
            ├── đọc/ghi MySQL trực tiếp
            └── gọi API đối với QR động và nghiệp vụ cần transaction

Flutter Mobile (Hội viên/PT)
            │
            ├── REST API
            └── WebSocket realtime

FastAPI Backend (Python)
            │
            ├── xác thực JWT
            ├── nghiệp vụ QR, lịch, check-in, thông báo
            ├── đọc outbox_events
            └── kết nối MySQL

MySQL/XAMPP: database gym_db dùng chung
```

### Vai trò

- **Admin:** toàn quyền Windows App.
- **Lễ tân:** dùng Windows App, không được xem các chức năng nhạy cảm dành riêng cho Admin.
- **PT:** đăng nhập Flutter, xem dashboard, hội viên phụ trách, lịch dạy, tự tạo/sửa/hủy lịch của mình, QR check-in.
- **Hội viên:** đăng nhập Flutter, xem gói tập, lịch tập, QR check-in, lịch sử, thông báo và hồ sơ.

---

## 2. Cấu trúc thư mục cuối cùng nên dùng

Đổi tên các thư mục sau khi giải nén để không bị lồng nhiều cấp `fixed_v3/fixed_v3`:

```text
C:\dev\Github\GymAppManager\
├── QlyPhongGym\
│   ├── app\
│   ├── migrations\
│   ├── requirements.txt
│   ├── apply_windows_schedule_patch.py
│   └── .env
│
├── core_strength_backend\
│   ├── app\
│   ├── database\
│   ├── docs\
│   ├── requirements.txt
│   ├── setup.bat
│   ├── run.bat
│   └── .env
│
└── core_strength_mobile\
    ├── lib\
    ├── tool\
    ├── pubspec.yaml
    ├── android\
    ├── web\
    └── windows\
```

### Bộ source nên dùng làm bản chuẩn

1. Windows App: source `QlyPhongGym` trong repository hiện tại.
2. Backend: dùng `core_strength_backend_fixed_v3`, sau đó chép đè `backend_schedule_patch`.
3. Flutter: dùng `core_strength_mobile_clean`, sau đó chép đè `flutter_schedule_patch`.
4. Database: dùng `gym_db_full_api.sql` trong backend.
5. Windows lịch: dùng `windows_schedule_patch` và chạy script vá một lần.

---

## 3. Phần mềm cần cài

- XAMPP có MySQL và phpMyAdmin.
- Python 3.11 hoặc 3.12.
- Flutter SDK và Dart SDK.
- Visual Studio Code.
- Chrome hoặc Edge để chạy Flutter Web.
- Android Studio nếu chạy Android Emulator.
- Visual Studio 2022 với workload Desktop development with C++ nếu chạy Flutter Windows.

Kiểm tra nhanh:

```powershell
python --version
flutter --version
flutter doctor
```

---

# PHẦN A — CÀI DATABASE

## 4. Khởi động MySQL

1. Mở XAMPP Control Panel.
2. Bấm **Start** tại MySQL.
3. Mở phpMyAdmin:

```text
http://localhost/phpmyadmin
```

## 5. Import database chuẩn

### Trường hợp cài mới, chưa có dữ liệu cần giữ

Import file:

```text
core_strength_backend\database\gym_db_full_api.sql
```

File này tạo lại database `gym_db`, toàn bộ bảng, dữ liệu mẫu, view và trigger realtime.

> Cảnh báo: file full có thể chứa `DROP DATABASE IF EXISTS gym_db`. Không import lại khi database đã có dữ liệu thật mà chưa sao lưu.

### Trường hợp đã có dữ liệu cần giữ

Không import lại file full. Chỉ import các migration còn thiếu:

```text
QlyPhongGym\migrations\add_training_schedules.sql
QlyPhongGym\migrations\add_schedule_realtime_triggers.sql
```

Chỉ chạy `add_training_schedules.sql` khi chưa có bảng `training_schedules`.

## 6. Kiểm tra database

Trong phpMyAdmin, chọn `gym_db` và kiểm tra các bảng chính:

```text
roles
users
receptionists
trainers
members
packages
member_packages
training_schedules
trainer_availability
qr_tokens
checkins
pt_sessions
transactions
payments
notifications
outbox_events
refresh_tokens
password_reset_otps
```

Database full hiện có 24 bảng, 3 view và trigger cho check-in, lịch, gói, thông báo và buổi PT.

## 7. Tài khoản dữ liệu mẫu

| Vai trò | Username | Mật khẩu |
|---|---|---|
| Admin | `admin` | `admin123` |
| Lễ tân | `receptionist` | `123456` |
| PT Flutter | `trainer` | `123456` |
| Hội viên Flutter | `member` | `123456` |

---

# PHẦN B — CÀI WINDOWS APP

## 8. Tạo file `.env` cho Windows App

Tạo file:

```text
QlyPhongGym\.env
```

Nội dung với XAMPP root không mật khẩu:

```env
DB_USER=root
DB_PASS=
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=gym_db
SECRET_KEY=replace-with-a-long-random-secret
```

Nếu MySQL có mật khẩu:

```env
DB_USER=root
DB_PASS=MAT_KHAU_MYSQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=gym_db
SECRET_KEY=replace-with-a-long-random-secret
```

## 9. Sửa môi trường ảo bị hỏng

Nếu thấy lỗi:

```text
No Python at '"D:\PythonSettings\python.exe'
```

thì `.venv` cũ đang trỏ tới Python không còn tồn tại. Chạy trong PowerShell:

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym

deactivate 2>$null

if (Test-Path .venv_broken) {
    Remove-Item .venv_broken -Recurse -Force
}

if (Test-Path .venv) {
    Rename-Item .venv .venv_broken
}

& "C:\Users\hakho\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu Python nằm chỗ khác, lấy đường dẫn bằng:

```powershell
where.exe python
```

## 10. Cài package Windows App

Các package chính gồm PyQt6, OpenCV, pyzbar, SQLAlchemy, PyMySQL, bcrypt, pandas, openpyxl và qrcode.

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Lỗi `pyzbar` thiếu DLL

Cài Visual C++ Redistributable x64. Nếu vẫn lỗi, có thể cần cài ZBar cho Windows hoặc tạm kiểm tra các phần không dùng camera trước.

## 11. Bổ sung tab lịch cho Windows App

Chép các file từ `windows_schedule_patch` vào `QlyPhongGym`, giữ nguyên cấu trúc.

Chạy một lần:

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python .\apply_windows_schedule_patch.py
```

Nếu `.venv` vẫn lỗi, chạy script bằng Python hệ thống:

```powershell
deactivate
& "C:\Users\hakho\AppData\Local\Programs\Python\Python312\python.exe" .\apply_windows_schedule_patch.py
```

Script tự thêm:

- Model `TrainingSchedule` vào `app/models.py`.
- Tab `Lịch tập & lịch dạy` vào `app/main.py`.
- File backup `.schedule_backup`.

Script có kiểm tra trùng, nhưng chỉ nên chạy khi đã chép đúng bản vá.

## 12. Chạy Windows App

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python -m app.main
```

Đăng nhập:

```text
admin / admin123
```

hoặc:

```text
receptionist / 123456
```

## 13. Chức năng Windows App

### Admin

- Dashboard quét QR.
- QR Demo.
- Lịch sử check-in.
- Quản lý lễ tân.
- Quản lý PT.
- Quản lý gói tập.
- Quản lý hội viên.
- Lịch tập và lịch dạy.
- Doanh thu, lương PT, lãi/lỗ.

### Lễ tân

- Dashboard và quét QR.
- QR Demo.
- Lịch sử check-in.
- Quản lý PT, gói, hội viên và lịch.
- Các chức năng chỉ Admin sẽ bị khóa hoặc ẩn.

### Tab lịch mới

- Tạo lịch cho PT và hội viên.
- Sửa lịch.
- Hủy lịch.
- Tìm kiếm theo PT, hội viên, SĐT hoặc nội dung.
- Lọc ngày và trạng thái.
- Chặn lịch trùng PT hoặc hội viên.
- Chỉ chọn được hội viên đang có gói PT phù hợp.

---

# PHẦN C — CÀI BACKEND FASTAPI

## 14. Chuẩn bị source backend

Dùng bản `core_strength_backend_fixed_v3`, đổi tên folder thành:

```text
core_strength_backend
```

Sau đó chép đè ba file từ `backend_schedule_patch`:

```text
app\api\routes\schedules.py
app\api\routes\trainers.py
app\schemas\schedule.py
```

## 15. Tạo môi trường backend

```powershell
cd C:\dev\Github\GymAppManager\core_strength_backend
.\setup.bat
```

Nếu muốn chạy thủ công:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 16. Tạo file `.env` backend

Copy `.env.example` thành `.env`:

```powershell
Copy-Item .env.example .env
```

Nội dung khuyến nghị cho môi trường local:

```env
APP_NAME=CORE STRENGTH API
APP_ENV=development
APP_DEBUG=true
API_PREFIX=/api
HOST=0.0.0.0
PORT=8000
TIMEZONE=Asia/Ho_Chi_Minh

DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/gym_db?charset=utf8mb4

SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY_123456789
QR_SECRET_KEY=CHANGE_THIS_TO_A_DIFFERENT_LONG_RANDOM_QR_KEY_987654321
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
QR_TOKEN_EXPIRE_SECONDS=30
PASSWORD_RESET_OTP_MINUTES=10

CORS_ORIGINS=*
OUTBOX_ENABLED=true
OUTBOX_POLL_SECONDS=1.0
OUTBOX_BATCH_SIZE=100

UPLOAD_DIR=uploads
PUBLIC_BASE_URL=http://127.0.0.1:8000
MAX_AVATAR_SIZE_MB=5
```

Nếu MySQL có mật khẩu:

```env
DATABASE_URL=mysql+pymysql://root:MAT_KHAU@127.0.0.1:3306/gym_db?charset=utf8mb4
```

Không dùng:

```env
DEBUG=release
```

Backend dùng:

```env
APP_DEBUG=true
```

## 17. Chạy backend

```powershell
cd C:\dev\Github\GymAppManager\core_strength_backend
.\run.bat
```

Khi thành công phải thấy:

```text
Uvicorn running on http://0.0.0.0:8000
Application startup complete.
```

Kiểm tra:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Kết quả `/health` phải cho biết API và database hoạt động.

## 18. Kiểm tra đăng nhập API bằng PowerShell

```powershell
$body = @{
    username = "member"
    password = "123456"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

Nếu đúng, kết quả có `access_token`, `refresh_token` và thông tin user.

## 19. Nhóm API chính

### Xác thực

```text
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/refresh
POST /api/auth/logout
POST /api/auth/forgot-password
POST /api/auth/reset-password
POST /api/auth/change-password
POST /api/windows/auth/login
```

### Mobile

```text
GET  /api/member/dashboard
GET  /api/trainer/dashboard
GET  /api/trainer/members
GET  /api/trainer/income
GET  /api/schedules
POST /api/schedules
PATCH /api/schedules/{id}
POST /api/qr/token
GET  /api/checkins/history
GET  /api/notifications
GET  /api/member/memberships
GET  /api/member/payments
GET  /api/profile
PATCH /api/profile
POST /api/profile/avatar
```

### Windows/QR

```text
POST /api/checkins/scan
POST /api/checkins/confirm
POST /api/checkins/confirm-pair
```

### Realtime

```text
WS /ws?token=<access_token>
```

---

# PHẦN D — CÀI FLUTTER MOBILE

## 20. Chuẩn bị source Flutter

1. Dùng `core_strength_mobile_clean` làm bản gốc.
2. Đổi tên thành `core_strength_mobile`.
3. Chép đè toàn bộ `lib` từ `flutter_schedule_patch` vào source Flutter.
4. Không dùng lại bản Flutter cũ có tự điền `member / 123456`.

Bản clean đã có:

- Không tự điền tài khoản/mật khẩu.
- Giao diện card/panel thống nhất.
- Đổi mật khẩu có mật khẩu hiện tại, mật khẩu mới và nhập lại mật khẩu mới.
- Quên mật khẩu có OTP, mật khẩu mới và nhập lại.
- Log Dio request/response nhưng che password/token.

## 21. Tạo các platform Flutter lần đầu

Tại folder Flutter:

```powershell
cd C:\dev\Github\GymAppManager\core_strength_mobile
.\tool\setup_project.bat
```

Hoặc thủ công:

```powershell
flutter create --project-name core_strength_mobile --org com.corestrength --platforms android,ios,web,windows .
flutter pub get
```

## 22. Kiểm tra source trước khi chạy

```powershell
flutter clean
flutter pub get
flutter analyze
```

Nếu `flutter analyze` còn lỗi thì sửa hết lỗi compile trước khi chạy.

## 23. Chạy Flutter trên Chrome

Backend phải đang chạy ở terminal khác.

PowerShell nên chạy một dòng:

```powershell
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

Không dùng `10.0.2.2` cho Chrome.

## 24. Chạy Flutter Windows

```powershell
flutter run -d windows --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

## 25. Chạy Android Emulator

```powershell
flutter run --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://10.0.2.2:8000/api --dart-define=WS_BASE_URL=ws://10.0.2.2:8000/ws
```

`10.0.2.2` là địa chỉ Android Emulator dùng để truy cập `localhost` của máy tính.

## 26. Chạy trên điện thoại thật

1. Máy tính và điện thoại phải cùng Wi-Fi.
2. Chạy:

```powershell
ipconfig
```

3. Tìm IPv4, ví dụ `192.168.1.20`.
4. Chạy Flutter:

```powershell
flutter run --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://192.168.1.20:8000/api --dart-define=WS_BASE_URL=ws://192.168.1.20:8000/ws
```

5. Cho phép Python/Uvicorn qua Windows Firewall.
6. Thử mở trên điện thoại:

```text
http://192.168.1.20:8000/health
```

## 27. Chạy mock chỉ để xem giao diện

```powershell
.\tool\run_mock.bat
```

Mock không đọc MySQL, không đồng bộ Windows App và không realtime.

---

# PHẦN E — THỨ TỰ CHẠY HÀNG NGÀY

## 28. Thứ tự chuẩn

### Bước 1 — XAMPP

Start MySQL.

### Bước 2 — Backend

Terminal 1:

```powershell
cd C:\dev\Github\GymAppManager\core_strength_backend
.\run.bat
```

### Bước 3 — Windows App

Terminal 2:

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python -m app.main
```

### Bước 4 — Flutter

Terminal 3, ví dụ Chrome:

```powershell
cd C:\dev\Github\GymAppManager\core_strength_mobile
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

`flutter run` không tự chạy backend.

---

# PHẦN F — HƯỚNG DẪN NGHIỆP VỤ

## 29. Tạo PT và hội viên

### Trên Windows App

1. Admin/lễ tân mở tab PT hoặc Hội viên.
2. Tạo tài khoản, nhập đầy đủ username, số điện thoại, ảnh và thông tin cá nhân.
3. Role trong bảng `users` phải đúng:
   - PT: `TRAINER`.
   - Hội viên: `MEMBER`.
4. Tài khoản phải `is_active = 1`.
5. PT phải có bản ghi trong `trainers`.
6. Hội viên phải có bản ghi trong `members`.

Nếu chỉ tạo `users` nhưng không tạo bản ghi `trainers`/`members`, mobile có thể đăng nhập nhưng dashboard và dữ liệu theo vai trò sẽ lỗi hoặc trống.

## 30. Gán gói tập cho hội viên

1. Mở tab Gói tập hoặc Hội viên.
2. Chọn gói.
3. Chọn hội viên.
4. Có thể chọn PT hoặc không chọn.
5. Nếu chọn PT, nhập số buổi và giá.
6. Xác nhận thanh toán.

Để PT thấy hội viên trong Flutter, `member_packages` phải thỏa mãn:

```text
pt_id = PT đang đăng nhập
status = active
start_date <= hôm nay
end_date >= hôm nay
sessions_remaining > 0 hoặc không giới hạn
```

## 31. PT tự lên lịch trên Flutter

1. Đăng nhập `trainer`.
2. Mở **Lịch dạy**.
3. Bấm **Tạo lịch**.
4. Chọn hội viên đang phụ trách.
5. Chọn ngày và giờ tương lai.
6. Nhập nội dung, địa điểm và ghi chú.
7. Lưu.

Backend sẽ:

- Tự lấy PT từ JWT.
- Kiểm tra hội viên thuộc PT.
- Kiểm tra gói còn hạn và còn buổi.
- Chặn trùng lịch PT.
- Chặn trùng lịch hội viên.
- Ghi lịch vào `training_schedules`.
- Phát sự kiện realtime.

## 32. Admin/lễ tân lên lịch trên Windows App

1. Mở **Lịch tập & lịch dạy**.
2. Chọn PT.
3. Chọn hội viên có gói PT phù hợp.
4. Chọn thời gian.
5. Nhập nội dung và lưu.
6. Lịch xuất hiện bên Flutter PT và hội viên qua realtime.

## 33. QR check-in đơn

### Flutter

1. Hội viên hoặc PT mở màn QR.
2. Flutter gọi `POST /api/qr/token`.
3. Backend trả token ký số, thời hạn khoảng 30 giây.
4. QR được hiển thị trên mobile.

### Windows App

Phần camera nên gửi token tới:

```text
POST /api/checkins/scan
```

để xem thông tin, sau đó xác nhận bằng:

```text
POST /api/checkins/confirm
```

Không nên tách QR động bằng chuỗi `member:1` hoặc `trainer:1`.

## 34. Quét đôi PT + hội viên

Windows App gửi hai token vào:

```text
POST /api/checkins/confirm-pair
```

Backend xử lý trong một transaction:

- Xác thực hai QR.
- Chặn token đã dùng.
- Kiểm tra gói.
- Kiểm tra PT phụ trách.
- Ghi check-in PT và hội viên.
- Trừ 1 buổi hội viên.
- Tạo buổi PT.
- Cộng KPI PT.
- Tính hoa hồng bằng 0,5% giá gói.
- Đánh dấu lịch gần nhất hoàn thành nếu phù hợp.
- Tạo thông báo.
- Phát WebSocket realtime.

## 35. Realtime hoạt động thế nào

- Flutter duy trì WebSocket `/ws?token=<JWT>`.
- Backend nhận thay đổi từ API hoặc đọc `outbox_events`.
- Trigger MySQL ghi sự kiện khi Windows App cập nhật trực tiếp database.
- Backend gửi sự kiện đến đúng user.
- Flutter tải lại dashboard, lịch, số buổi, lịch sử hoặc thông báo.

Các sự kiện chính:

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

## 36. Đổi mật khẩu

Flutter có đủ 3 trường:

1. Mật khẩu hiện tại.
2. Mật khẩu mới.
3. Nhập lại mật khẩu mới.

App kiểm tra:

- Không để trống.
- Mật khẩu mới đủ độ dài.
- Mật khẩu mới khác mật khẩu hiện tại.
- Hai lần nhập phải trùng nhau.

Sau đó gọi:

```text
POST /api/auth/change-password
```

## 37. Quên mật khẩu

Luồng hiện tại:

```text
Nhập username/email/SĐT
→ gọi forgot-password
→ nhận OTP
→ nhập OTP
→ nhập mật khẩu mới hai lần
→ reset-password
```

Trong development, backend có thể trả `debug_otp` để test.

Chưa có nhà cung cấp email/SMS thật. Khi triển khai production phải tích hợp SMTP, SendGrid, Twilio hoặc dịch vụ SMS khác và đặt:

```env
APP_DEBUG=false
```

---

# PHẦN G — CHECKLIST KIỂM TRA TOÀN HỆ THỐNG

## 38. Kiểm tra cơ bản

- [ ] XAMPP MySQL đang chạy.
- [ ] Database `gym_db` tồn tại.
- [ ] Backend `/health` trả thành công.
- [ ] Swagger `/docs` mở được.
- [ ] API đăng nhập trả token.
- [ ] Windows App đăng nhập được Admin/Lễ tân.
- [ ] Flutter đăng nhập được Hội viên/PT.
- [ ] Flutter không chạy mock.
- [ ] Chrome dùng `127.0.0.1`, không dùng `10.0.2.2`.
- [ ] Android Emulator dùng `10.0.2.2`.
- [ ] Điện thoại thật dùng IPv4 máy tính.
- [ ] PT thấy danh sách hội viên phụ trách.
- [ ] PT tạo được lịch.
- [ ] Windows thấy lịch vừa tạo.
- [ ] Hội viên thấy lịch realtime.
- [ ] QR được tạo và hết hạn.
- [ ] Quét QR chỉ ghi một lần.
- [ ] Quét đôi trừ buổi và cộng KPI.
- [ ] Thông báo xuất hiện sau check-in/lịch.

## 39. Test realtime lịch

1. Chạy backend.
2. Đăng nhập PT trên Flutter.
3. Đăng nhập hội viên ở cửa sổ khác hoặc thiết bị khác.
4. PT tạo lịch.
5. Hội viên phải nhận lịch mới mà không cần đăng nhập lại.
6. Mở Windows App để đối chiếu cùng bản ghi.

## 40. Test realtime khi Windows ghi trực tiếp DB

1. Đảm bảo `OUTBOX_ENABLED=true`.
2. Đảm bảo có bảng `outbox_events`.
3. Đảm bảo đã import trigger lịch/check-in/gói.
4. Sửa hoặc tạo lịch trong Windows App.
5. Kiểm tra `outbox_events` có bản ghi mới.
6. Backend phải đánh dấu event đã xử lý.
7. Flutter phải tải lại dữ liệu tương ứng.

---

# PHẦN H — LỖI THƯỜNG GẶP

## 41. `No module named uvicorn`

Nguyên nhân: chạy nhầm `.venv` hoặc chưa cài backend requirements.

```powershell
cd C:\dev\Github\GymAppManager\core_strength_backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\run.bat
```

Đường dẫn Python đúng phải nằm trong folder backend.

## 42. `ZoneInfoNotFoundError: Asia/Ho_Chi_Minh`

```powershell
.\.venv\Scripts\python.exe -m pip install tzdata
```

`tzdata` đã có trong requirements bản v3.

## 43. `debug Input should be a valid boolean ... release`

Xóa biến cũ:

```env
DEBUG=release
```

Dùng:

```env
APP_DEBUG=true
```

Bản v3 cũng tự tránh xung đột biến `DEBUG` từ Code Runner.

## 44. Flutter không đăng nhập và không có log

- Chạy bản clean/login-fixed.
- Bảo đảm `USE_MOCK_DATA=false`.
- Kiểm tra terminal Flutter có dòng POST login.
- Kiểm tra terminal backend có request `/api/auth/login`.
- Mở `/health` trên cùng thiết bị đang chạy Flutter.

## 45. Chrome vẫn gọi `10.0.2.2`

Dừng app hoàn toàn; hot reload không thay `dart-define`.

```powershell
flutter clean
flutter pub get
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

## 46. Dio thiếu `transformTimeout`

Trong switch `DioExceptionType`, thêm:

```dart
DioExceptionType.transformTimeout =>
  'Quá thời gian xử lý dữ liệu phản hồi từ máy chủ.',
```

Bản clean mới đã sửa lỗi này.

## 47. `const ListView` compile lỗi

Đổi:

```dart
const ListView(
```

thành:

```dart
ListView(
```

Bản clean mới đã sửa.

## 48. Flutter báo connection refused

Kiểm tra theo thứ tự:

1. Backend đang chạy.
2. `/health` mở được.
3. URL đúng theo thiết bị.
4. Port 8000 chưa bị chặn.
5. Firewall cho phép Python.
6. Điện thoại và máy tính cùng mạng.

## 49. PT không thấy hội viên khi tạo lịch

Kiểm tra bảng `member_packages`:

```sql
SELECT *
FROM member_packages
WHERE pt_id = <TRAINER_ID>;
```

Bản ghi phải còn hạn, active và còn buổi.

## 50. Tab lịch không xuất hiện trên Windows

Kiểm tra:

```text
QlyPhongGym\app\ui\tab_schedules.py
QlyPhongGym\app\ui\schedule_form.py
```

Chạy:

```powershell
python .\apply_windows_schedule_patch.py
```

Kiểm tra `app/main.py` có dòng module `app.ui.tab_schedules`.

## 51. Database báo thiếu bảng

Nếu cài mới, import lại `gym_db_full_api.sql` sau khi sao lưu.

Nếu giữ dữ liệu cũ, chỉ chạy migration thiếu, không drop database.

## 52. Backend chạy nhưng database disconnected

Kiểm tra `.env`:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/gym_db?charset=utf8mb4
```

Kiểm tra MySQL XAMPP, tên database, mật khẩu và cổng 3306.

---

# PHẦN I — QUY TẮC PHÁT TRIỂN TIẾP

## 53. Không cho Flutter kết nối trực tiếp MySQL

Flutter chỉ dùng REST API và WebSocket. Không đưa tài khoản MySQL vào app mobile.

## 54. Nghiệp vụ nhiều bước phải qua backend

Các nghiệp vụ sau phải qua API và transaction:

- Quét đôi.
- Trừ buổi.
- Cộng KPI.
- Tính hoa hồng.
- Đổi mật khẩu.
- Tạo QR động.
- Refresh token.

## 55. Windows App có thể ghi DB trực tiếp ở chức năng CRUD

Các thao tác CRUD cũ có thể tiếp tục ghi trực tiếp MySQL, nhưng cần trigger outbox để Flutter nhận realtime.

Riêng QR động nên gọi API backend để xác thực token đúng và chống quét trùng.

## 56. Không lưu mật khẩu dạng plain text

Chỉ lưu bcrypt hash. Không log password, access token, refresh token hoặc OTP production.

## 57. Không hard-code tài khoản demo vào Flutter

Các ô login phải để trống. Tài khoản demo chỉ được ghi trong tài liệu hoặc dữ liệu mẫu.

## 58. Sao lưu trước khi thay schema

Sao lưu bằng phpMyAdmin hoặc lệnh:

```powershell
mysqldump -u root gym_db > gym_db_backup.sql
```

Nếu root có mật khẩu:

```powershell
mysqldump -u root -p gym_db > gym_db_backup.sql
```

---

# PHẦN J — TRẠNG THÁI HIỆN TẠI VÀ PHẦN CHƯA HOÀN THIỆN SẢN XUẤT

## 59. Đã có

- Windows App Admin/Lễ tân.
- Flutter Hội viên/PT Clean Architecture.
- FastAPI REST API.
- JWT và refresh token.
- QR động dùng một lần.
- Check-in đơn và quét đôi.
- Lịch PT tự tạo.
- Windows quản lý lịch.
- Realtime WebSocket + outbox.
- Dashboard, hồ sơ, lịch sử, gói, thu nhập PT.
- Đổi mật khẩu và quên mật khẩu theo OTP test.

## 60. Chưa phải production hoàn chỉnh

- OTP chưa gửi email/SMS thật; development dùng `debug_otp`.
- Backend có lưu device token nhưng chưa cấu hình dịch vụ Firebase Admin để gửi push khi app đóng.
- HTTPS chưa cấu hình.
- Secret trong `.env` cần đổi trước khi triển khai.
- CORS đang để `*` cho development.
- MySQL XAMPP chỉ phù hợp local/demo; production cần MySQL server được bảo vệ và sao lưu.
- Camera Windows cần chuyển toàn bộ luồng QR động sang API nếu vẫn còn parser QR demo cũ.
- Cần kiểm thử giao dịch đồng thời, mất mạng, retry và dữ liệu trùng trước khi dùng thật.

---

# 61. Lệnh chạy nhanh mỗi ngày

## Terminal 1 — Backend

```powershell
cd C:\dev\Github\GymAppManager\core_strength_backend
.\run.bat
```

## Terminal 2 — Windows App

```powershell
cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python -m app.main
```

## Terminal 3 — Flutter Chrome

```powershell
cd C:\dev\Github\GymAppManager\core_strength_mobile
flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
```

## Dừng hệ thống

- Flutter: nhấn `q` hoặc `Ctrl + C`.
- Backend: `Ctrl + C`.
- Windows App: đóng cửa sổ.
- XAMPP: Stop MySQL sau cùng.

hạy lại toàn bộ hệ thống

Backend:

cd C:\dev\Github\GymAppManager\core_strength_backend
.\run.bat

Windows App:

cd C:\dev\Github\GymAppManager\QlyPhongGym
.\.venv\Scripts\Activate.ps1
python -m app.main

Flutter Chrome:

cd C:\dev\Github\GymAppManager\core_strength_mobile

flutter clean
flutter pub get

flutter run -d chrome --dart-define=USE_MOCK_DATA=false --dart-define=API_BASE_URL=http://127.0.0.1:8000/api --dart-define=WS_BASE_URL=ws://127.0.0.1:8000/ws
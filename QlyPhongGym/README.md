# Quản lý Phòng Gym (Windows)

Hướng dẫn nhanh cài đặt và chạy (Windows, XAMPP):

1. Cài XAMPP và tạo một MySQL database (ví dụ `gym_db`).
2. Tạo file `.env` trong thư mục gốc với biến:

```
DB_USER=root
DB_PASS=
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=gym_db
SECRET_KEY=your-secret
```

3. Cài Python và tạo virtualenv, sau đó cài dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Chạy migration SQL `migrations/schema.sql` trên MySQL để tạo bảng mẫu.
5. Chạy ứng dụng:

```powershell
python -m app.main
```

Ghi chú: giao diện và chức năng đang ở dạng scaffold. Tiếp theo sẽ triển khai chi tiết các tab, xác thực, và luồng quét QR.

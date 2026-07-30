# API contract cho CORE STRENGTH Mobile

Prefix mặc định: `/api`

## 1. Đăng nhập

### `POST /auth/login`

Request:

```json
{
  "username": "member",
  "password": "123456"
}
```

Response:

```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "user": {
    "id": 1,
    "username": "member",
    "full_name": "Nguyễn Văn A",
    "phone": "0987654321",
    "email": "member@example.com",
    "avatar": null,
    "role": "MEMBER"
  }
}
```

Role mobile hỗ trợ: `MEMBER`, `TRAINER` hoặc `PT`.

### `GET /auth/me`

Header:

```text
Authorization: Bearer <access_token>
```

Trả về object user hoặc `{ "user": {...} }`.

### `POST /auth/forgot-password`

```json
{
  "account": "0987654321"
}
```

## 2. Dashboard hội viên

### `GET /member/dashboard`

```json
{
  "membership": {
    "package_name": "Gói GYM Gold",
    "start_date": "2026-05-15",
    "end_date": "2026-08-25",
    "sessions_remaining": 12,
    "progress": 0.75,
    "trainer_name": "PT Minh Quân",
    "status": "Còn hạn"
  },
  "monthly_checkins": 9,
  "upcoming_sessions": [
    {
      "id": 1,
      "title": "Tập Ngực - Vai",
      "participant_name": "PT Minh Quân",
      "start_at": "2026-07-30T18:00:00",
      "end_at": "2026-07-30T19:30:00",
      "status": "upcoming",
      "location": "Khu PT tầng 2",
      "note": null
    }
  ],
  "recent_activities": [
    {
      "id": 1,
      "title": "Check-in thành công",
      "subtitle": "Lễ tân xác nhận tại quầy chính",
      "occurred_at": "2026-07-29T18:05:00",
      "type": "checkin"
    }
  ]
}
```

## 3. Dashboard PT

### `GET /trainer/dashboard`

```json
{
  "is_working": true,
  "stats": {
    "today_sessions": 5,
    "assigned_members": 12,
    "monthly_sessions": 80,
    "estimated_income": 12500000
  },
  "today_sessions": [],
  "alerts": [
    {
      "member_name": "Lê Hoàng Nam",
      "message": "Sắp hết buổi tập, còn 2 buổi",
      "severity": "warning",
      "sessions_remaining": 2
    }
  ]
}
```

## 4. Lịch tập/lịch dạy

### `GET /schedules?role=MEMBER`

Response là một JSON array:

```json
[
  {
    "id": 21,
    "title": "Tập Ngực",
    "participant_name": "PT Minh Quân",
    "start_at": "2026-07-30T17:30:00",
    "end_at": "2026-07-30T19:00:00",
    "status": "upcoming",
    "location": "Khu tập chính",
    "note": "Ưu tiên bài đẩy ngực"
  }
]
```

Status: `upcoming`, `completed`, `cancelled`.

## 5. QR Check-in

### `POST /qr/token`

Request:

```json
{
  "entity_type": "MEMBER"
}
```

Response:

```json
{
  "token": "signed-one-time-token",
  "expires_at": "2026-07-29T23:10:30+07:00"
}
```

Token phải:

- Có thời hạn ngắn khoảng 20–30 giây.
- Chỉ dùng một lần.
- Không chứa ID thuần mà không có chữ ký.
- Sau khi Windows App xác nhận phải đánh dấu `used_at`.

## 6. Lịch sử Check-in

### `GET /checkins/history`

```json
[
  {
    "id": 1,
    "scanned_at": "2026-07-29T18:05:00",
    "location": "Quầy check-in chính",
    "status": "Thành công",
    "source": "QR Mobile"
  }
]
```

## 7. Hội viên PT phụ trách

### `GET /trainer/members`

```json
[
  {
    "id": 1,
    "full_name": "Nguyễn Văn A",
    "phone": "0987654321",
    "package_name": "Gold + PT 30 buổi",
    "end_date": "2026-08-25",
    "sessions_remaining": 12
  }
]
```

## 8. Thông báo

### `GET /notifications`

```json
[
  {
    "id": 1,
    "title": "Check-in thành công",
    "body": "Buổi check-in đã được lễ tân xác nhận.",
    "created_at": "2026-07-29T18:05:00",
    "type": "checkin",
    "is_read": false
  }
]
```

## 9. WebSocket

Kết nối:

```text
ws://SERVER:8000/ws?token=<JWT>
```

Message:

```json
{
  "type": "checkin.confirmed",
  "received_at": "2026-07-29T18:05:03+07:00",
  "payload": {
    "checkin_id": 125,
    "member_id": 1,
    "scanned_at": "2026-07-29T18:05:00+07:00"
  }
}
```

Backend nên gửi sự kiện đến đúng user thay vì broadcast dữ liệu cá nhân cho toàn bộ client.

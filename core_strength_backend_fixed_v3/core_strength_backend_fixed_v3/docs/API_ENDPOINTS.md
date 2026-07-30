# Danh sách endpoint

## Xác thực

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `POST /api/auth/change-password`
- `POST /api/windows/auth/login`

## Mobile Hội viên/PT

- `GET /api/member/dashboard`
- `GET /api/trainer/dashboard`
- `GET /api/trainer/members`
- `GET /api/trainer/income`
- `GET /api/schedules`
- `POST /api/qr/token`
- `GET /api/checkins/history`
- `GET /api/notifications`
- `PATCH /api/notifications/{id}/read`
- `POST /api/notifications/read-all`
- `GET /api/packages`
- `GET /api/member/memberships`
- `GET /api/member/payments`
- `GET /api/member/requests`
- `POST /api/member/requests`
- `GET /api/profile`
- `PATCH /api/profile`
- `POST /api/profile/avatar`
- `POST /api/devices/token`
- `DELETE /api/devices/token`

## Windows/Staff

- `POST /api/checkins/scan`
- `POST /api/checkins/confirm`
- `POST /api/checkins/confirm-pair`
- `POST /api/schedules`
- `PATCH /api/schedules/{id}`

## Hệ thống

- `GET /health`
- `GET /docs`
- `WS /ws?token=<JWT>`

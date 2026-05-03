# notification-service

Microservice quản lý **thông báo người dùng** (in-app + email).

- Port: `8084`.
- Database: `notification_db`.
- Loại thông báo: `budget_exceeded`, `large_transaction`, `anomaly_detected`, `report_ready`, `system`.

## Trạng thái: skeleton

Đã có:

- `Notification` entity + Flyway migration.
- Spring Boot Application + Eureka client + Config client + Mail starter + Feign.

## TODO

- `NotificationRepository`, `NotificationService`, `NotificationController`:
  - `GET /api/notifications?unreadOnly=true&page=0&size=20` (Spring Data pagination).
  - `POST /api/notifications/{id}/read` (mark read).
  - `POST /api/notifications/read-all`.
  - `DELETE /api/notifications/{id}`.
- `EmailService` dùng `JavaMailSender`, render template (Thymeleaf hoặc plain text).
- Feign client `AuthClient` lấy email user từ `auth-service`.
- Lắng nghe sự kiện vượt ngân sách (sau khi thêm message broker — ban đầu dùng REST POST từ `budget-service`).
- `JwtAuthenticationFilter`, `SecurityConfig`, `GlobalExceptionHandler`.

## Chạy local

```bash
mvn -pl services/notification-service -am spring-boot:run
```

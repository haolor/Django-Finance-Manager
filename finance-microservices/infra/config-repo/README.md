# config-repo

Thư mục này được mount (read-only) vào `config-server` ở `/app/config-repo`. Spring Cloud Config Server (profile `native`) đọc các file ở đây để phục vụ tất cả service.

## Quy ước file

- `application.yml` — cấu hình **chung** cho mọi service (logging, actuator).
- `<service-name>.yml` — override theo service. Ví dụ `auth-service.yml`.
- `<service-name>-<profile>.yml` — override theo profile. Ví dụ `auth-service-prod.yml`.

## Lưu ý

- **Không** đặt secret (JWT_SECRET, password, API key) vào đây nếu repo được commit. Truyền qua biến môi trường trong `docker-compose.yml`.
- Khi đổi file: gọi `POST http://<service>/actuator/refresh` (cần `spring-cloud-starter-bus` để broadcast) hoặc restart service đó.

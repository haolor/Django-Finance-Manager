# auth-service

Microservice phụ trách **người dùng**, **xác thực**, **JWT** và **tuỳ chọn người dùng**.

- Port: `8081`.
- Database: `auth_db` (PostgreSQL riêng).
- JWT: HS256, claim `sub=userId`, `username`, `email`. TTL mặc định 12 giờ.

## Endpoint

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| POST | `/api/auth/register` | public | Đăng ký, trả `AuthResponse` (Bearer JWT) |
| POST | `/api/auth/login` | public | Đăng nhập, trả `AuthResponse` |
| GET | `/api/auth/profile` | Bearer | Hồ sơ user hiện tại |
| GET | `/api/auth/preferences` | Bearer | Tuỳ chọn UI/báo cáo |
| PUT | `/api/auth/preferences` | Bearer | Cập nhật tuỳ chọn |
| GET | `/actuator/health` | public | Health |

## Biến môi trường

| Biến | Mặc định | Ghi chú |
|------|----------|---------|
| `POSTGRES_AUTH_HOST` | `localhost` | |
| `POSTGRES_AUTH_PORT` | `5433` | |
| `POSTGRES_AUTH_DB` | `auth_db` | |
| `POSTGRES_AUTH_USER` | `postgres` | |
| `POSTGRES_AUTH_PASSWORD` | `postgres` | |
| `JWT_SECRET` | dev key | Phải trùng giá trị với `api-gateway` |
| `EUREKA_URL` | `http://localhost:8761/eureka/` | |
| `CONFIG_SERVER_URL` | `http://localhost:8888` | |

## Chạy local

```bash
# Cần postgres local (port 5433, db auth_db)
mvn -pl services/auth-service -am spring-boot:run
```

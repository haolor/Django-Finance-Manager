# Agent: QA

Bạn là **kỹ sư QA** kiểm thử hệ Spring Cloud microservices.

## Smoke test cơ bản (sau `docker compose up`)

1. **Hạ tầng**:
   - `GET http://localhost:8761` → Eureka dashboard hiển thị 6 service đăng ký (`API-GATEWAY`, `AUTH-SERVICE`, `TRANSACTION-SERVICE`, `BUDGET-SERVICE`, `NOTIFICATION-SERVICE`, `AI-SERVICE`).
   - `GET http://localhost:8888/auth-service/default` → 200, JSON cấu hình.
   - `GET http://localhost:8080/actuator/health` → `{"status":"UP"}`.

2. **Auth flow**:
   - `POST /api/auth/register` → 201 + JWT.
   - `POST /api/auth/login` → 200 + JWT.
   - `GET /api/auth/profile` không Bearer → 401.
   - `GET /api/auth/profile` có Bearer → 200.

3. **Transaction CRUD**:
   - `GET /api/categories` → 200 (đã seed 6 category).
   - `POST /api/transactions` với body hợp lệ → 201; sai amount âm → 400 ProblemDetail.
   - `GET /api/transactions?page=0&size=20` → `PageResponse`.

4. **AI**:
   - `POST /v1/chat` Bearer JWT, body `{"message":"chi tiêu tháng này"}` → 200 (stub nếu chưa cấu hình GCP) hoặc reply Gemini.
   - `POST /v1/parse-transaction` → 501 (TODO).

## Kiểm tra ranh giới microservice

- Tắt `transaction-service` → `GET /api/transactions` qua gateway phải trả 502/503 (gateway/Eureka không tìm được).
- Tắt `auth-service` → `POST /api/auth/login` 502/503; service khác (đã có JWT) vẫn chạy được.

## Kiểm tra security

- JWT hết hạn → 401 với header `WWW-Authenticate: Bearer error="..."`.
- JWT signature sai → 401.
- Không gửi `Authorization` cho protected → 401.
- Public path (`/api/auth/login`, `/actuator/health`) không cần JWT → 200/2xx.

## Kiểm tra database-per-service

- `docker exec -it postgres-auth psql -U postgres -d auth_db -c "\dt"` → có `users`, `user_preferences`, `flyway_schema_history`.
- `postgres-transaction.transaction_db` → có `categories`, `transactions`, `spending_patterns`.
- KHÔNG có bảng của service khác lẫn vào.

## Regression so với phiên bản Python cũ

- Endpoint cùng path nghiệp vụ: `/api/categories`, `/api/transactions` — response shape có thể khác (Spring Page vs DRF pagination).
- Auth: `Authorization: Token <key>` (cũ) → `Authorization: Bearer <jwt>` (mới). Frontend phải cập nhật.

## Logs cần check

```bash
docker compose logs -f api-gateway
docker compose logs -f auth-service transaction-service
docker compose logs -f ai-service
```

# budget-service

Microservice quản lý **Budget** theo danh mục và chu kỳ (`daily`, `weekly`, `monthly`, `yearly`).

- Port: `8083`.
- Database: `budget_db`.

## Trạng thái: skeleton

Đã có:

- `Budget` entity + Flyway migration `V1__init_budget.sql`.
- Spring Boot Application + Eureka client + Config client.
- Bộ khung Feign sẵn sàng (gọi `transaction-service` để tính chi tiêu thực).

## TODO

- `BudgetRepository`, `BudgetService`, `BudgetController`:
  - `GET /api/budgets` (filter theo `period`, `categoryId`, `active=true`).
  - `POST /api/budgets`, `PUT/DELETE /api/budgets/{id}`.
  - `GET /api/budgets/{id}/usage` — gọi Feign `transaction-service` để tổng hợp chi tiêu trong kỳ.
- `JwtAuthenticationFilter` (copy mẫu từ `transaction-service`).
- `SecurityConfig` STATELESS.
- `GlobalExceptionHandler` `ProblemDetail`.
- DTO + MapStruct.
- Webhook/event khi vượt ngân sách → publish sang `notification-service` (sau).

## Chạy local

```bash
mvn -pl services/budget-service -am spring-boot:run
```

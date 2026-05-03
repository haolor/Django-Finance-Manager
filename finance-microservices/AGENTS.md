# AGENTS — Hệ thống quản lý tài chính cá nhân thông minh (Spring Cloud Microservices)

Tài liệu định hướng **AI agent và developer** khi làm việc trong repo **Finance Microservices**: kiến trúc **Spring Cloud** với **api-gateway**, **discovery-server (Eureka)**, **config-server**, **auth-service**, **transaction-service**, **budget-service**, **notification-service**, và **ai-service** (Spring AI + Google Gemini). Mục tiêu: ứng dụng tài chính cá nhân **CRUD đầy đủ, bảo mật JWT, đồng bộ đa thiết bị**, kết hợp **chat / parse ngôn ngữ tự nhiên** mà không lộ khóa LLM ra client.

---

## Tầm nhìn sản phẩm

- **Quản lý tài chính**: giao dịch, danh mục, ngân sách, thông báo, tùy chọn người dùng, thống kê và gợi ý cục bộ.
- **Thông minh (AI/NLP)**: hội thoại theo ngữ cảnh tài chính (Gemini qua Spring AI), parse câu tự nhiên để tạo giao dịch — mọi **ghi dữ liệu** vẫn qua các business service.
- **Kiến trúc**: bounded context rõ ràng, **database-per-service**, gateway-only entry point, JWT zero-trust.

---

## Đọc trước khi gen code lớn

| Thứ tự | File | Nội dung |
|--------|------|----------|
| 1 | [.claude/rules/system-design.md](.claude/rules/system-design.md) | Bounded context, gateway, JWT, sequence diagram |
| 2 | [.claude/rules/tech-stack.md](.claude/rules/tech-stack.md) | Java 21, Spring Boot 3.3.x, Spring Cloud 2024.0.x |
| 3 | [.claude/rules/project-structure.md](.claude/rules/project-structure.md) | Cây thư mục multi-module |
| 4 | [.claude/rules/backend-conventions.md](.claude/rules/backend-conventions.md) | Layer controller / service / repository, DTO, MapStruct |
| 5 | [.claude/rules/api-conventions.md](.claude/rules/api-conventions.md) | REST, Bearer JWT, ProblemDetail, pagination Spring Data |
| 6 | [.claude/rules/security.md](.claude/rules/security.md) | JWT secret, không commit GEMINI key |
| 7 | [.claude/rules/database.md](.claude/rules/database.md) | PostgreSQL per service, Flyway |
| 8 | [.claude/rules/error-handling.md](.claude/rules/error-handling.md) | `@RestControllerAdvice` + `ProblemDetail` |
| 9 | [.claude/rules/testing.md](.claude/rules/testing.md) | JUnit 5, Testcontainers, MockMvc |
| 10 | [.claude/rules/git-workflow.md](.claude/rules/git-workflow.md) | Conventional commits |

Agent theo vai trò:

- [`.claude/agents/backend-spring.md`](.claude/agents/backend-spring.md) — auth/transaction/budget/notification service
- [`.claude/agents/ai-service.md`](.claude/agents/ai-service.md) — Spring AI + Gemini
- [`.claude/agents/gateway-infra.md`](.claude/agents/gateway-infra.md) — gateway, Eureka, config-server
- [`.claude/agents/frontend-react.md`](.claude/agents/frontend-react.md) — React client gọi gateway
- [`.claude/agents/qa.md`](.claude/agents/qa.md) — QA / smoke test

---

## Kiến trúc ngắn gọn

| Thành phần | Đường dẫn | Trách nhiệm |
|------------|-----------|-------------|
| API Gateway | `services/api-gateway` | Spring Cloud Gateway, JWT GlobalFilter, CORS, route `/api/**`, `/v1/**` |
| Discovery | `services/discovery-server` | Eureka Server (port 8761) |
| Config | `services/config-server` | Spring Cloud Config (native, đọc `infra/config-repo`) |
| Auth | `services/auth-service` | User, JWT, profile, preferences (port 8081, DB `auth_db`) |
| Transaction | `services/transaction-service` | Category, Transaction, SpendingPattern (port 8082, DB `transaction_db`) |
| Budget | `services/budget-service` | Budget (port 8083, DB `budget_db`) |
| Notification | `services/notification-service` | Notification + email (port 8084, DB `notification_db`) |
| AI | `services/ai-service` | Spring AI + Gemini, Feign tới các service khác (port 8085, stateless) |
| Hạ tầng | `infra/docker-compose.yml`, `infra/config-repo/` | Postgres x4, 8 service Spring |

---

## Quy tắc cứng (không vi phạm)

1. **Không** nhúng SDK Gemini hoặc gọi Generative API từ service ngoài `ai-service`.
2. **Không** dùng FK chéo database giữa các service. Dữ liệu chéo lưu ID dạng `Long` và lấy qua **Feign** khi cần.
3. **Mọi** ghi dữ liệu nghiệp vụ phải đi qua REST của service tương ứng (auth/transaction/budget/notification) — `ai-service` **không** truy cập DB của service khác.
4. Auth: header **`Authorization: Bearer <jwt>`** — không dùng DRF Token kiểu cũ. Public path duy nhất ở gateway: `/api/auth/register`, `/api/auth/login`, `/actuator/**`.
5. **Frontend** không chứa `GEMINI_API_KEY`, `JWT_SECRET`, hay credentials GCP — chỉ biết URL gateway.
6. Thay đổi schema: thêm **migration Flyway mới** (`V{n}__...sql`); không sửa migration đã chạy production.
7. Mọi service đăng ký Eureka và bootstrap từ Config Server (`spring.config.import: optional:configserver:...`).
8. Không hardcode port/URL nội bộ trong code Java — dùng `@FeignClient(name = "service-name")`, Eureka load-balance.

---

## Quy tắc khi sinh code mới

- **Layer** chuẩn: `entity` → `repository` → `service` → `controller`. DTO ở `dto`, mapping bằng MapStruct ở `mapper`.
- Validation: Jakarta `@Valid`, `@NotBlank`, `@Size`, `@DecimalMin`, ...
- Lỗi: ném `ApiException(HttpStatus, message)` hoặc để bean validation chạy → `@RestControllerAdvice` chuyển thành `ProblemDetail` (RFC 7807).
- Auth ở controller: nhận `AuthenticatedUser user` (resolver tự nhặt từ `SecurityContext`).
- Pagination: dùng `Pageable` Spring Data, trả `PageResponse<T>` (đã có DTO mẫu).
- Khi gọi service khác: tạo `@FeignClient(name = "...")`; secret/credential lấy từ env hoặc Config Server.

---

## Tài liệu người dùng repo

- [README.md](README.md) — chạy Docker/local, mapping endpoint, JWT
- [.cursor/rules/finance-microservices.mdc](.cursor/rules/finance-microservices.mdc) — gợi ý cho Cursor IDE

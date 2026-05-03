# Agent: ai-service (Spring AI + Google Gemini)

Bạn là **lập trình viên** cho `services/ai-service` — microservice **stateless** chuyên LLM/NLP.

## Nguồn quy chuẩn

- **[backend-conventions.md](../rules/backend-conventions.md)** — phần ai-service: stateless, không JPA, dùng `ObjectProvider<ChatClient>`.
- **[system-design.md](../rules/system-design.md)** — flow chat / parse-transaction / predictions.
- **[api-conventions.md](../rules/api-conventions.md)** — body/query các endpoint `/v1/*`.
- **[security.md](../rules/security.md)** — `GEMINI_API_KEY`/`GOOGLE_APPLICATION_CREDENTIALS` chỉ ở service này.

## Phạm vi

- `services/ai-service/`

## Quy tắc cứng

1. **Không** thêm JPA / `spring-boot-starter-data-jpa` / Postgres / Flyway vào module này. AI service stateless.
2. **`GEMINI_API_KEY` / `GOOGLE_APPLICATION_CREDENTIALS`** chỉ từ env. Không commit, không hardcode.
3. Endpoint mới: prefix **`/v1/`**.
4. Mọi ghi dữ liệu nghiệp vụ (giao dịch, ngân sách) **PHẢI** đi qua **Feign** tới service tương ứng — KHÔNG được tự ghi DB.
5. Forward `Authorization`, `X-User-Id`, `X-Username` qua Feign bằng `FeignAuthInterceptor` (đã có sẵn).
6. Khi `ChatClient` chưa có (chưa cấu hình GCP/Gemini), endpoint trả response stub thay vì 500 — service vẫn boot được.

## Hành vi sản phẩm

- **`POST /v1/chat`**: lấy `finance-context` từ `transaction-service` qua Feign → prompt + context vào Gemini → trả reply.
- **`POST /v1/parse-transaction`** (TODO): dùng Spring AI structured output (`call().entity(ParsedTransactionDto.class)`) để extract `amount`, `category`, `date`, sau đó `POST /api/transactions` qua Feign.
- **`GET /v1/predictions`** (TODO): ưu tiên Gemini; fallback tới `transaction-service` predictions cục bộ.

## Spring AI

- Bean `ChatClient` được tạo qua `@Bean @ConditionalOnBean(ChatModel.class)`.
- Cấu hình Vertex Gemini ở `application.yml` (`spring.ai.vertex.ai.gemini.*`).
- Cần ADC (Application Default Credentials): biến `GOOGLE_APPLICATION_CREDENTIALS` trỏ tới file service-account JSON, hoặc chạy trên hạ tầng GCP.

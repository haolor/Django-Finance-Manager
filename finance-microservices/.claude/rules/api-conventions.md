# Quy ước API — Core (Django DRF) & AI (FastAPI)

Chuẩn hóa **định dạng**, **header**, **endpoint**, và **hợp đồng lỗi** giữa client và hai service.

---

## 1. Core API — prefix `/api/`

### 1.1 Chung

- **Định dạng**: JSON, mã hóa **UTF-8**.
- **Content-Type** request có body: `application/json` (trừ upload file theo endpoint OCR/multipart).
- **Version path**: hiện **không** bắt buộc `v1` trên toàn bộ Core (giữ tương thích client/mobile). Endpoint mới có thể dùng `/api/v2/` nếu breaking change được kiểm soát.

### 1.2 Lỗi (DRF)

- Thường gặp: `{ "detail": "Thông báo lỗi." }`.
- Lỗi validation serializer: object với key là tên field, giá trị là danh sách chuỗi lỗi.
- HTTP status: 400 (validation), 401 (chưa auth), 403 (không quyền), 404, 500 theo chuẩn HTTP.

### 1.3 Phân trang

- Query: `page`, `page_size` (theo cấu hình DRF project).
- Response kiểu paginated: `count`, `next`, `previous`, `results` (tùy class pagination).

### 1.4 Auth

```http
Authorization: Token <token_string>
```

---

## 2. AI Service — versioning `/v1/`

### 2.1 Health

- **`GET /health`**: readiness (cho orchestrator/load balancer).

### 2.2 Chat

- **`POST /v1/chat`**
  - **Headers**: `Authorization: Token <user_token>`, `Content-Type: application/json`
  - **Body** (tối thiểu): `{ "message": "Nội dung người dùng" }`
  - **Hành vi**: service gọi Core (ví dụ `GET /api/ai/finance-context/`) rồi Gemini; client không gửi Gemini key.

### 2.3 Predictions (LLM + fallback)

- **`GET /v1/predictions`**
  - **Headers**: `Authorization: Token <user_token>`
  - **Query**: `start_date`, `end_date` định dạng **`YYYY-MM-DD`**
  - **Hành vi**: ưu tiên Gemini; lỗi/mất key có thể fallback sang Core local — xem README mapping.

### 2.4 Parse transaction (NLP)

- **`POST /v1/parse-transaction`**
  - **Headers**: `Authorization: Token <user_token>`
  - **Body**: `{ "text": "Cà phê 45k chiều nay" }`
  - **Hành vi**: AI suy luận → tạo giao dịch qua Core (`POST` transactions hoặc endpoint tương đương), không ghi DB trực tiếp.

### 2.5 Lỗi (FastAPI)

- Giữ mặc định FastAPI/Starlette: `{"detail": ...}` cho nhiều lỗi HTTP.
- Khi refactor thống nhất toàn hệ, có thể bọc envelope — mục 4.

---

## 3. Service-to-service (AI → Core)

- Luôn kèm **token của user** (forward từ client), không dùng shared service secret cho truy cập dữ liệu cá nhân trừ khi thiết kế lại.
- Base URL Core trên AI: biến `CORE_API_BASE_URL` (Docker: hostname service nội bộ).

### 3.1 Correlation (khuyến nghị sau này)

- Client gửi tùy chọn: `X-Request-ID: <uuid>`
- Core và AI log cùng id để trace — cần middleware.

---

## 4. Envelope lỗi thống nhất (khi refactor — gợi ý)

Hiện tại giữ format DRF/FastAPI mặc định. Khi chuẩn hóa:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Mô tả ngắn cho người dùng / developer",
    "field": "amount"
  }
}
```

Frontend nên có hàm `parseApiError(response)` tách hai kiểu trong giai đoạn chuyển tiếp.

---

## 5. Mapping nhanh từ monolith

| Monolith | Microservice |
|----------|----------------|
| `POST /api/chatbot/` | `POST {AI}/v1/chat` |
| NLP tạo giao dịch | `POST {AI}/v1/parse-transaction` |
| Predictions Gemini | `GET {AI}/v1/predictions` |
| Predictions chỉ local | `GET {CORE}/api/ai/predictions/` |
| Ngữ cảnh cho LLM | `GET {CORE}/api/ai/finance-context/` (thường AI gọi, không phải FE) |

Chi tiết: [README.md](../../README.md).

---

## 6. Tài liệu liên quan

- [backend-conventions.md](backend-conventions.md) — phân tầng Django/FastAPI
- [frontend-conventions.md](frontend-conventions.md) — hai base URL và Token
- [security.md](security.md) — không lộ secret

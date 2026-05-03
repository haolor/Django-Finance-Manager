# Quy ước API — REST qua API Gateway

Chuẩn hóa **định dạng**, **header**, **endpoint**, **paging**, **lỗi** giữa client và toàn hệ thống.

---

## 1. Entry point duy nhất

- Client chỉ biết **một** base URL = `api-gateway` (mặc định `http://localhost:8080`).
- `api-gateway` route theo path:
  - `/api/auth/**` → `auth-service`
  - `/api/categories/**`, `/api/transactions/**` → `transaction-service`
  - `/api/budgets/**` → `budget-service`
  - `/api/notifications/**` → `notification-service`
  - `/v1/**` → `ai-service`

---

## 2. Định dạng

- **JSON UTF-8**.
- `Content-Type: application/json` cho request có body.
- Date/time:
  - `LocalDate` → `YYYY-MM-DD`.
  - `Instant` → ISO 8601 với `Z` (UTC).
  - `BigDecimal` → string số (Jackson default), tránh mất chính xác.

---

## 3. Auth

```http
Authorization: Bearer <jwt>
```

- JWT phát hành bởi `auth-service` (HS256, claim `sub=userId`, `username`, `email`, `iat`, `exp`).
- Public path (không cần JWT): `/api/auth/register`, `/api/auth/login`, `/actuator/health`, `/actuator/info`.
- Hết hạn → `401 Unauthorized` với header `WWW-Authenticate: Bearer error="Invalid token"`.

---

## 4. Lỗi — RFC 7807 ProblemDetail

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Dữ liệu không hợp lệ",
  "errors": {
    "amount": "must be greater than or equal to 0.01"
  }
}
```

Status convention:

| Status | Khi nào |
|--------|---------|
| `400` | Validation `@Valid`, body sai |
| `401` | Thiếu / sai JWT |
| `403` | JWT đúng nhưng không đủ quyền (chưa dùng nhiều) |
| `404` | Resource không tồn tại / không thuộc user |
| `409` | Conflict (username/email trùng) |
| `502` | Lỗi service downstream (Feign) |
| `503` | Provider AI chưa cấu hình |

---

## 5. Pagination — Spring Data

Query param chuẩn `Pageable`:

- `?page=0&size=20&sort=transactionDate,desc`

Response wrap bằng `PageResponse<T>`:

```json
{
  "content": [...],
  "page": 0,
  "size": 20,
  "totalElements": 137,
  "totalPages": 7,
  "first": true,
  "last": false
}
```

---

## 6. Endpoint chính

### 6.1 auth-service

| Method | Path | Body | Status |
|--------|------|------|--------|
| POST | `/api/auth/register` | `RegisterRequest` | 201 |
| POST | `/api/auth/login` | `LoginRequest` | 200 |
| GET | `/api/auth/profile` | — | 200 |
| GET | `/api/auth/preferences` | — | 200 |
| PUT | `/api/auth/preferences` | `UserPreferencesDto` | 200 |

### 6.2 transaction-service

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/api/categories` | List |
| POST | `/api/categories` | Create (201) |
| GET/PUT/DELETE | `/api/categories/{id}` | Detail / Update / Delete (204) |
| GET | `/api/transactions?categoryId=&fromDate=&toDate=&page=&size=&sort=` | PageResponse |
| POST | `/api/transactions` | Create (201) |
| GET/PUT/DELETE | `/api/transactions/{id}` | Của user hiện tại |

### 6.3 ai-service

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/v1/chat` | `{ "message": "..." }` → reply |
| POST | `/v1/parse-transaction` | `{ "text": "..." }` (501 — TODO) |
| GET | `/v1/predictions?startDate=&endDate=` | TODO |

---

## 7. Header bổ sung

| Header | Hướng | Ai set | Ý nghĩa |
|--------|-------|--------|---------|
| `Authorization` | client → gateway | client | Bearer JWT |
| `X-User-Id` | gateway → service | gateway | userId từ claim `sub` |
| `X-Username` | gateway → service | gateway | username từ claim |
| `X-Request-ID` | client → gateway → service | client (optional) | Trace ID; khuyến nghị thêm filter MDC sau |

---

## 8. Versioning

- Endpoint nghiệp vụ: prefix `/api/`.
- Endpoint AI: prefix `/v1/` (đã version sẵn).
- Breaking change: phát hành `/api/v2/...` thay vì sửa contract cũ.

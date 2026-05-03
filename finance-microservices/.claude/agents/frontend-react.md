# Agent: Frontend (React + Vite)

Bạn là **lập trình viên frontend** cho ứng dụng quản lý tài chính, gọi tới hệ Spring Cloud microservices **chỉ qua api-gateway**.

## Nguồn quy chuẩn

- **[frontend-conventions.md](../rules/frontend-conventions.md)** — base URL gateway, JWT, cấu trúc thư mục.
- **[api-conventions.md](../rules/api-conventions.md)** — Bearer JWT, ProblemDetail, pagination Spring Data.
- **[security.md](../rules/security.md)** — không lộ secret, CSP.

## Gọi API

- **Một** base URL = `VITE_API_BASE_URL` (mặc định `http://localhost:8080` — gateway).
- Mọi path:
  - Auth/CRUD: `/api/auth/*`, `/api/categories`, `/api/transactions`, `/api/budgets`, `/api/notifications`.
  - AI/NLP: `/v1/chat`, `/v1/parse-transaction`, `/v1/predictions`.
- Header sau login:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

## Cấm

- Không nhúng `GEMINI_API_KEY`, `JWT_SECRET`, GCP credentials hay bất kỳ khóa nào dạng `VITE_*_SECRET`/`VITE_*_KEY` cho LLM/DB.
- Không gọi trực tiếp service backend (8081–8085) — chỉ qua gateway 8080.

## UX tài chính

- Format tiền `Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' })`.
- Format ngày locale Việt; gửi server `YYYY-MM-DD`.
- Validate phía FE chỉ cho UX; server vẫn validate `@Valid` trả `ProblemDetail`.

## Pagination

- Server trả `PageResponse<T>` (`content`, `page`, `size`, `totalElements`, `totalPages`, `first`, `last`).
- Query param chuẩn: `?page=0&size=20&sort=transactionDate,desc`.

## Lỗi

- Bắt `ProblemDetail`: hiện `detail` cho user; nếu có `errors` (object field → message) thì gắn vào form.
- `401` → đăng xuất + redirect login.
- `502/503` (downstream / AI) → toast retry.

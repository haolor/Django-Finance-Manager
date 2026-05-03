# Quy ước Frontend — React + Vite (gọi qua API Gateway)

Tài liệu chuẩn hóa **client web/mobile-web** tương tác với hệ Spring Cloud microservices. Repo frontend có thể nằm ngoài `finance-microservices/` nhưng phải tuân các quy tắc dưới.

---

## 1. Công nghệ tham chiếu

| Hạng mục | Lựa chọn | Ghi chú |
|----------|----------|---------|
| Framework | React 18+ | Functional components, hooks |
| Build | Vite | Env prefix `VITE_` |
| Styling | Tailwind CSS | Design tokens nhất quán |
| Routing | React Router | Bảo vệ route cần đăng nhập |
| HTTP | `fetch` / axios | **Một** lớp `apiClient` tập trung |
| State | React Query khuyến nghị cho list/detail | |

---

## 2. Biến môi trường

```env
VITE_API_BASE_URL=http://localhost:8080
```

**Một** base URL duy nhất = `api-gateway`. Frontend KHÔNG biết các service backend riêng lẻ.

CẤM tuyệt đối:

- `VITE_GEMINI_API_KEY`
- `VITE_JWT_SECRET`
- `VITE_<...>_PRIVATE_*`

---

## 3. Xác thực — JWT Bearer

1. Sau `POST /api/auth/login` lưu `token` từ `AuthResponse`.
2. Mọi request gắn header:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

3. Lưu token: ưu tiên **memory + httpOnly cookie** qua BFF; nếu chưa có BFF thì `localStorage` (chấp nhận rủi ro XSS) + giảm TTL token.
4. `401` → đăng xuất phía client (xóa token, redirect login).

---

## 4. Phân luồng gọi API (qua gateway)

| Nghiệp vụ | Path |
|-----------|------|
| Đăng ký / đăng nhập / profile / preferences | `${VITE_API_BASE_URL}/api/auth/...` |
| Category, Transaction | `${VITE_API_BASE_URL}/api/categories`, `/api/transactions` |
| Budget | `${VITE_API_BASE_URL}/api/budgets` |
| Notification | `${VITE_API_BASE_URL}/api/notifications` |
| Chat AI / parse / predictions | `${VITE_API_BASE_URL}/v1/chat`, `/v1/parse-transaction`, `/v1/predictions` |

---

## 5. Cấu trúc thư mục gợi ý (feature-based)

```
src/
  app/                   # providers, router, layout
  features/
    auth/
    transactions/
    budgets/
    notifications/
    chat/
  shared/
    api/                 # apiClient.ts, interceptors (gắn Bearer)
    components/
    hooks/
    lib/                 # format tiền, date theo locale
  assets/
```

---

## 6. Pagination

Server trả `PageResponse<T>`:

```json
{ "content": [...], "page": 0, "size": 20, "totalElements": 137, "totalPages": 7, "first": true, "last": false }
```

Client gửi: `?page=0&size=20&sort=transactionDate,desc`.

---

## 7. Xử lý lỗi

- Server trả `ProblemDetail` (RFC 7807): `{ status, title, detail, errors? }`.
- Hiển thị `detail` cho user; với 400 + `errors` map về form field.

```ts
type ProblemDetail = {
  status: number;
  title: string;
  detail: string;
  errors?: Record<string, string>;
};
```

---

## 8. Format

- Tiền: `Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' })`.
- Ngày: `Intl.DateTimeFormat('vi-VN')` hoặc `dayjs`.
- Gửi `LocalDate` lên server: `YYYY-MM-DD`.

---

## 9. Bảo mật UI

- Không log token / PII ra `console` ở production build.
- CSP: hạn chế inline script.
- Validate input phía FE chỉ cho UX; server vẫn validate `@Valid`.

---

## 10. Tóm tắt một dòng

**Một base URL = gateway. Một header = `Authorization: Bearer <jwt>`. Không có khóa LLM trên trình duyệt.**

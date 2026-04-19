# Quy ước Frontend — Ứng dụng tài chính cá nhân (React + Vite)

Tài liệu này chuẩn hóa **client web/mobile-web** tương tác với **Core API** và **AI/NLP Service** trong kiến trúc microservice. Repo frontend có thể nằm ngoài `finance-microservices/` nhưng **phải tuân** các quy tắc dưới đây để đồng bộ với backend hiện tại.

---

## 1. Công nghệ tham chiếu

| Hạng mục | Lựa chọn | Ghi chú |
|----------|----------|---------|
| Framework | React 18+ | Functional components, hooks |
| Build | Vite | Env prefix `VITE_` |
| Styling | Tailwind CSS | Design tokens/spacing thống nhất |
| Routing | React Router | Bảo vệ route cần đăng nhập |
| HTTP | `fetch` hoặc axios | Một lớp `apiClient` tập trung |
| State | Context / Zustand / React Query (tuỳ dự án) | Ưu tiên cache có thời hạn cho danh sách giao dịch |

---

## 2. Biến môi trường (bắt buộc ý nghĩa)

Đặt trong `.env` / `.env.example` của frontend (không commit secret):

| Biến | Ví dụ | Mục đích |
|------|-------|----------|
| `VITE_CORE_API_URL` | `http://localhost:8000/api` | Base URL **có suffix `/api`** — mọi CRUD, auth, OCR, sync |
| `VITE_AI_API_URL` | `http://localhost:8001` | Base URL AI service **không** thêm `/api` — path kiểu `/v1/chat` |

**Không** định nghĩa `VITE_GEMINI_API_KEY` hoặc bất kỳ khóa LLM nào trên frontend.

---

## 3. Xác thực (Token DRF)

- Sau `POST /api/auth/login/` (Core), lưu token theo cơ chế an toàn của app (memory + `httpOnly` cookie nếu có BFF; hoặc `localStorage` chỉ khi chấp nhận rủi ro XSS — ưu tiên giảm thời gian sống token và CSP).
- Mọi request tới Core và AI (khi user đã đăng nhập) gửi header:

```http
Authorization: Token <token_string>
Content-Type: application/json
```

- **401**: đăng xuất client-side hoặc refresh flow (nếu sau này có); không lặp vô hạn cùng một request.

---

## 4. Phân luồng gọi API

| Nghiệp vụ | Service | Ví dụ endpoint |
|-----------|---------|----------------|
| Đăng ký/đăng nhập, CRUD giao dịch, danh mục, ngân sách, thông báo, upload OCR | **Core** | `${VITE_CORE_API_URL}/transactions/` … |
| Chat AI, dự đoán LLM (nếu dùng), parse câu tiếng Việt/Anh thành giao dịch | **AI** | `${VITE_AI_API_URL}/v1/chat`, `/v1/predictions`, `/v1/parse-transaction` |
| Ngữ cảnh tài chính cho LLM | **Core** (AI service gọi nội bộ) | FE **không** gọi trực tiếp trừ khi có màn debug; bình thường chỉ AI gọi `GET /api/ai/finance-context/` |

Mapping chi tiết monolith → microservices: [README.md](../../README.md) và [api-conventions.md](api-conventions.md).

---

## 5. Cấu trúc thư mục gợi ý (feature-based)

```
src/
  app/                 # providers, router, layout
  features/
    auth/
    transactions/
    budgets/
    chat/              # UI chat → chỉ gọi VITE_AI_API_URL
  shared/
    api/               # coreClient.ts, aiClient.ts, interceptors
    components/
    hooks/
    lib/               # format tiền tệ, date theo locale
  assets/
```

- **Format tiền**: dùng `Intl.NumberFormat` hoặc thư viện đã chọn; không hardcode ký hiệu sai locale.
- **Ngày gửi lên API**: theo contract backend (thường `YYYY-MM-DD` cho query range).

---

## 6. Đặt tên và component

| Loại | Quy ước | Ví dụ |
|------|---------|-------|
| Component file | PascalCase | `TransactionList.tsx` |
| Hooks | camelCase + `use` prefix | `useTransactions.ts` |
| API modules | theo domain | `transactionsApi.ts` |
| Hằng số route | `UPPER_SNAKE` hoặc object frozen | `ROUTES.TRANSACTIONS` |

Tránh logic nghiệp vụ tài chính phức tạp trong JSX; tách hooks/services.

---

## 7. Xử lý lỗi và loading

- **Core (DRF)**: lỗi thường `{ "detail": "..." }` hoặc lỗi theo field serializer — hiển thị message thân thiện, không leak stack trace.
- **AI (FastAPI)**: hiển thị lỗi mạng/timeout rõ ràng; có retry có giới hạn cho chat nếu cần.
- Trạng thái loading: skeleton hoặc spinner trên vùng ảnh hưởng; tránh chặn toàn app trừ khi bắt buộc.

---

## 8. Bảo mật & privacy UI

- Không log token hoặc PII đầy đủ ra `console` trong production build.
- Form nhập số tiền: validate min/max hợp lý; cảnh báo khi vượt ngân sách (nếu có dữ liệu local).
- Tuân [security.md](security.md) phía backend; phía FE: CSP, không inline script không cần thiết khi deploy.

---

## 9. Accessibility & i18n (khuyến nghị)

- Nhãn form, `aria-*` cho modal và live region cho thông báo lỗi chat.
- Chuẩn bị tách chuỗi UI (Việt/Anh) nếu sản phẩm mở rộng — key ổn định, không nhúng HTML trong chuỗi dịch.

---

## 10. Kiểm thử frontend

- Unit: utils format tiền/ngày.
- Integration: mock Core/AI với MSW hoặc Vitest + fetch mock.
- E2E (tùy): luồng login → tạo giao dịch → mở chat (cần env test).

---

## Tóm tắt một dòng

**Core = dữ liệu & nghiệp vụ; AI = LLM & NLP; FE = hai base URL + một Token — không bao giờ có Gemini key trên trình duyệt.**

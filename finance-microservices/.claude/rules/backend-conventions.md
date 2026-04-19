# Quy ước Backend — Core (Django DRF) & AI (FastAPI)

Tài liệu chuẩn hóa **định dạng code, API, phân tầng** cho hai service trong hệ **quản lý tài chính cá nhân thông minh** tách microservice.

---

## Phần A — Core API (`services/core-api`)

### A.1 Vai trò

- **Nguồn sự thật** cho User, Category, Transaction, Budget, Notification, UserPreferences, SpendingPattern.
- **REST JSON** toàn bộ CRUD, auth token, đồng bộ, OCR receipt, thống kê cục bộ (`/api/ai/trends`, `/api/ai/anomalies`, `/api/ai/savings-suggestions`, `/api/ai/predictions` phiên bản không Gemini).
- **`GET /api/ai/finance-context/`**: JSON tổng hợp phục vị AI service (Gemini) — gọi kèm token user.

### A.2 Stack & cấu hình

- Python 3.12+, Django 6, Django REST Framework, PostgreSQL.
- Auth: `rest_framework.authtoken` — header `Authorization: Token <key>`.
- CORS: `django-cors-headers` — cấu hình origin frontend và (nếu cần) origin AI service khi gọi server-to-server từ trình duyệt không áp dụng; **AI service gọi Core từ server** bằng `httpx` + token forward.

### A.3 Cấu trúc Django

- App chính (ví dụ `finance/`): `models.py`, `serializers.py`, `views.py` hoặc `viewsets.py`, `urls.py`, `permissions.py`, `migrations/`.
- Project package (ví dụ `coresite/`): `settings.py`, `urls.py`, `wsgi.py`.
- **Không** đặt gọi Gemini trong Core; không import SDK Google Generative AI trong settings của Core.

### A.4 Quy ước REST

- Tiền tố URL: `/api/` (tương thích mobile hiện có).
- JSON UTF-8; thời gian ISO 8601 nếu có `DateTimeField`; ngày theo field `DateField` thường `YYYY-MM-DD`.
- Lỗi DRF: `{"detail": "..."}` hoặc object lỗi theo field từ serializer — giữ nhất quán với client đang dùng.
- Phân trang: `page`, `page_size` theo cấu hình DRF (mặc định project).

### A.5 Serializer & validation

- Mọi input user qua serializer; validate số tiền không âm (trừ khi nghiệp vụ cho chi/thu có ký hiệu riêng — thống nhất một convention).
- `read_only` cho field hệ thống (`id`, `created_at`, …).

### A.6 Migrations

- Mỗi thay đổi schema: `makemigrations` + commit file migration.
- **Không** chỉnh sửa file migration đã merge/chạy production; tạo migration mới để sửa.

### A.7 Bảo mật Core

- Không commit `DJANGO_SECRET_KEY`, DB password, `.env`.
- Production: `DEBUG=False`, `ALLOWED_HOSTS` rõ ràng — xem [security.md](security.md).

---

## Phần B — AI / NLP Service (`services/ai-nlp-service`)

### B.1 Vai trò

- **FastAPI + Uvicorn**: chat Gemini, predictions có LLM (fallback Core khi lỗi), **parse NLP** → tạo giao dịch qua `POST` tới Core (không ghi DB trực tiếp).
- HTTP client: **`httpx`** — module kiểu `core_client.py` encapsulate gọi Core.

### B.2 Versioning URL

- Endpoint công khai: **`/v1/...`** (ví dụ `POST /v1/chat`, `GET /v1/predictions`, `POST /v1/parse-transaction`).
- `GET /health` cho readiness.

### B.3 Auth

- Mọi endpoint cần ngữ cảnh user: header `Authorization: Token <user_token>` (forward từ client).
- **Không** dùng shared secret thay thế token người dùng cho dữ liệu cá nhân trừ khi thiết kế lại bảo mật.

### B.4 Secrets

- Chỉ env **`GEMINI_API_KEY`** (và cấu hình model nếu có) trên AI service.
- **`CORE_API_BASE_URL`** trỏ tới Core (ví dụ `http://core-api:8000` trong Docker).

### B.5 Code layout

- `app/main.py`: đăng ký router, CORS nếu cần, exception handlers.
- `app/config.py`: Settings pydantic từ env.
- `app/core_client.py`: hàm `get_finance_context`, `create_transaction`, … — tái sử dụng.
- `app/gemini_client.py`: gọi API Google.
- `app/nlp_service.py`: logic parse text → payload gọi Core.

### B.6 Type hints & lỗi

- Gợi ý type hints cho hàm public và model Pydantic request/response.
- Phản hồi lỗi: giữ FastAPI mặc định hoặc chuẩn hóa sau — đã ghi trong [api-conventions.md](api-conventions.md).

---

## Phần C — Giao tiếp giữa hai service

| Hướng | Cách | Ghi chú |
|-------|------|---------|
| Client → Core | HTTPS REST + Token | CRUD, login |
| Client → AI | HTTPS REST + Token | Chat, parse, predictions |
| AI → Core | Server-side HTTP + **cùng Token user** | Không bypass auth cho dữ liệu riêng tư |

**Correlation ID (tùy chọn)**: client có thể gửi `X-Request-ID`; middleware hai bên có thể log cùng giá trị (thêm sau).

---

## Phần D — Phong cách code Python (chung)

- PEP 8, indent 4 spaces; import: stdlib → third-party → local.
- Định dạng: Ruff/Black nếu đã có trong CI — xem [code-style.md](code-style.md).
- [clean-code.md](clean-code.md), [error-handling.md](error-handling.md) áp dụng cho cả hai service nơi phù hợp.

---

## Tóm tắt ranh giới

| Việc | Core | AI |
|------|------|-----|
| ORM / PostgreSQL | Có | Không (cho business data) |
| Gemini | Không | Có |
| Token user | Phát hành & xác thực | Forward tới Core |

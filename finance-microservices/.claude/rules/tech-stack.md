# Tech stack — Hệ quản lý tài chính cá nhân (Microservices)

Tài liệu tổng hợp **công nghệ** và **giới hạn** từng service để tránh lệch stack khi phát triển hoặc gen code.

---

## 1. Core API (`services/core-api`)

| Thành phần | Công nghệ | Ghi chú |
|------------|-----------|---------|
| Ngôn ngữ | Python 3.12+ | |
| Framework web | Django 6 | Project package (ví dụ `coresite/`) |
| API | Django REST Framework | JSON, ViewSet/Generic views tùy module |
| Auth | `rest_framework.authtoken` | Header `Authorization: Token <key>` |
| CSDL | PostgreSQL | Một DB cho Core hiện tại |
| CORS | `django-cors-headers` | Cho phép origin frontend dev/prod |
| Migration | `django.db.migrations` | Không sửa file migration đã production |

**Không** tích hợp SDK Google Generative AI / Gemini trong Core — xem [system-design.md](system-design.md).

---

## 2. AI / NLP Service (`services/ai-nlp-service`)

| Thành phần | Công nghệ | Ghi chú |
|------------|-----------|---------|
| Ngôn ngữ | Python 3.12+ | |
| Framework | FastAPI | OpenAPI tự động tại `/docs` |
| Server | Uvicorn | ASGI |
| HTTP client | `httpx` | Gọi Core; async/sync tùy code hiện có |
| LLM | Google Gemini (Generative Language API) | Biến môi trường `GEMINI_API_KEY` |

**Không** dùng Django ORM, không kết nối PostgreSQL của Core cho nghiệp vụ người dùng — xem [backend-conventions.md](backend-conventions.md).

**Không** giả định có Celery/Redis trừ khi đã thêm vào `infra/` và `requirements.txt`.

---

## 3. Client (tham chiếu — repo frontend có thể tách)

| Thành phần | Công nghệ | Ghi chú |
|------------|-----------|---------|
| UI | React | Hooks, functional components |
| Build | Vite | Prefix env: `VITE_*` |
| CSS | Tailwind CSS | Thống nhất spacing, màu, typography |
| Gọi API | `fetch` / axios + lớp bọc | Hai base URL: Core `/api`, AI `/v1` |

Biến môi trường chuẩn:

- `VITE_CORE_API_URL` — ví dụ `http://localhost:8000/api`
- `VITE_AI_API_URL` — ví dụ `http://localhost:8001`

Chi tiết đặt tên route, error handling, bảo mật: [frontend-conventions.md](frontend-conventions.md).

---

## 4. Hạ tầng & vận hành

| Thành phần | Ghi chú |
|------------|---------|
| Docker Compose | `infra/docker-compose.yml` — PostgreSQL + Core + AI |
| Reverse proxy (tương lai) | TLS, rate limit — [security.md](security.md) |

---

## 5. Công cụ phát triển (gợi ý)

- Format/lint Python: Ruff / Black khi đưa vào CI — [code-style.md](code-style.md).
- Type hints: ưu tiên module tích hợp ngoài (AI: Pydantic, client Core).

---

## 6. Ma trận “được phép / không được”

| Công nghệ | Core | AI |
|-----------|------|-----|
| Django ORM | Có | Không |
| PostgreSQL (app DB) | Có | Không (business data) |
| Gemini API | Không | Có |
| httpx gọi Core | Không cần (đã trong process) | Có |

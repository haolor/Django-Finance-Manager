# AGENTS — Hệ thống quản lý tài chính cá nhân thông minh (Microservices)

Tài liệu này định hướng **AI agent và developer** khi làm việc trong repo **Finance Microservices**: tách **Core API (Django + DRF + PostgreSQL)** và **AI/NLP Service (FastAPI + Gemini)**. Mục tiêu là ứng dụng tài chính cá nhân có **CRUD đầy đủ, bảo mật, đồng bộ đa thiết bị**, kết hợp **chat/parse ngôn ngữ tự nhiên** mà không làm lộ khóa LLM ra client.

---

## Tầm nhìn sản phẩm

- **Quản lý tài chính**: giao dịch, danh mục, ngân sách, thông báo, tùy chọn người dùng, thống kê và gợi ý (một phần cục bộ trên Core).
- **Thông minh (AI/NLP)**: hội thoại theo ngữ cảnh tài chính (Gemini), dự đoán/gợi ý nâng cao khi có LLM, **phân tích câu tự nhiên** để tạo giao dịch — mọi **ghi dữ liệu** vẫn qua Core API.
- **Kiến trúc**: microservice theo ranh giới rõ: **dữ liệu và nghiệp vụ tài chính = Core**; **orchestration LLM + NLP = AI service** (HTTP tới Core với token người dùng).

---

## Đọc trước khi gen code lớn

Thứ tự gợi ý:

| Thứ tự | File | Nội dung |
|--------|------|----------|
| 1 | [.claude/rules/system-design.md](.claude/rules/system-design.md) | Ranh giới service, luồng, dữ liệu |
| 2 | [.claude/rules/backend-conventions.md](.claude/rules/backend-conventions.md) | Quy chuẩn Django DRF, FastAPI, migration |
| 3 | [.claude/rules/frontend-conventions.md](.claude/rules/frontend-conventions.md) | Quy chuẩn React/Vite, gọi API, env |
| 4 | [.claude/rules/api-conventions.md](.claude/rules/api-conventions.md) | REST AI service, Token, mapping endpoint |
| 5 | [.claude/rules/security.md](.claude/rules/security.md) | Secret, production, không lộ Gemini ra FE |
| 6 | [.claude/rules/database.md](.claude/rules/database.md) | PostgreSQL, migration |
| 7 | [.claude/rules/testing.md](.claude/rules/testing.md) | Kiểm thử |
| 8 | [.claude/rules/git-workflow.md](.claude/rules/git-workflow.md) | Nhánh, PR |

Agent theo vai trò:

- [`.claude/agents/backend-django.md`](.claude/agents/backend-django.md) — Core Django
- [`.claude/agents/ai-nlp-service.md`](.claude/agents/ai-nlp-service.md) — FastAPI AI
- [`.claude/agents/frontend-react.md`](.claude/agents/frontend-react.md) — React client

---

## Kiến trúc ngắn gọn

| Thành phần | Đường dẫn | Trách nhiệm |
|------------|-----------|-------------|
| **Core API** | `services/core-api` | Django DRF, PostgreSQL, Token auth, ORM, migrations, toàn bộ REST `/api/`, thống kê cục bộ, OCR, `GET /api/ai/finance-context/` |
| **AI / NLP** | `services/ai-nlp-service` | FastAPI, Gemini (chat, predictions), `POST /v1/parse-transaction`; gọi Core bằng **HTTP + token user** — **không** Django ORM |
| **Hạ tầng** | `infra/docker-compose.yml` | PostgreSQL + hai service |

---

## Quy tắc cứng (không vi phạm)

1. **Không** nhúng **Gemini** hoặc gọi Generative API từ **Core** — LLM chỉ trong AI service.
2. **AI service không** dùng Django ORM hay kết nối DB trực tiếp cho nghiệp vụ người dùng; mọi thao tác dữ liệu qua Core HTTP API.
3. Endpoint chat legacy monolith `POST /api/chatbot/` → client dùng AI: **`POST /v1/chat`** (base URL AI service).
4. **Frontend** không chứa `GEMINI_API_KEY`; chỉ Core URL + AI URL + Token sau login.
5. Thay đổi schema: **migration mới**, không sửa migration đã áp dụng production.

---

## Tài liệu người dùng repo

- [README.md](README.md) — chạy Docker/local, mapping endpoint, liên kết monolith
- [.cursor/rules/finance-microservices.mdc](.cursor/rules/finance-microservices.mdc) — gợi ý cho Cursor AI

Chi tiết định dạng request/response và convention: **backend** → [backend-conventions.md](.claude/rules/backend-conventions.md); **frontend** → [frontend-conventions.md](.claude/rules/frontend-conventions.md).

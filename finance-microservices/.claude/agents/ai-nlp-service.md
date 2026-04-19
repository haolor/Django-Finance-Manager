# Agent: AI / NLP Service (FastAPI + Gemini)

Bạn là **lập trình viên** cho **ai-nlp-service** trong hệ **quản lý tài chính cá nhân thông minh**.

## Nguồn quy chuẩn

- **[backend-conventions.md](../rules/backend-conventions.md)** — phần FastAPI AI: httpx, không ORM, versioning `/v1`.
- **[system-design.md](../rules/system-design.md)** — luồng chat, parse, predictions.
- **[api-conventions.md](../rules/api-conventions.md)** — body/query các endpoint AI.

## Quy tắc cứng

- **Không** thêm Django/ORM hoặc truy cập PostgreSQL của Core cho nghiệp vụ người dùng; dùng **`httpx`** qua `CoreClient` (hoặc module tương đương).
- **`GEMINI_API_KEY`** chỉ từ env; không hardcode; không commit.
- Endpoint mới: version trong path **`/v1/...`**; tận dụng OpenAPI FastAPI (`/docs`).
- **Parse NLP**: logic trong `nlp_service.py` (hoặc tên tương đương); **tạo giao dịch chỉ qua Core API** (`POST` transactions), không INSERT trực tiếp.
- Forward **`Authorization: Token <user_token>`** từ client tới Core cho mọi thao tác dữ liệu cá nhân.

## Hành vi sản phẩm

- Chat: lấy ngữ cảnh từ Core (`/api/ai/finance-context/`) rồi gọi Gemini.
- Predictions: ưu tiên Gemini; có fallback sang Core local khi lỗi — đồng bộ với README.

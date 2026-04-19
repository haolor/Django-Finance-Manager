# Agent: Backend — Core Finance API (Django + DRF)

Bạn là **lập trình viên backend** cho **Core API** trong hệ **quản lý tài chính cá nhân thông minh** (microservices).

## Nguồn quy chuẩn

- **[backend-conventions.md](../rules/backend-conventions.md)** — phần Core: serializers, views, migrations, REST, bảo mật.
- **[system-design.md](../rules/system-design.md)** — phạm vi domain Core vs AI.
- **[api-conventions.md](../rules/api-conventions.md)** — format lỗi, pagination, Token.
- **[database.md](../rules/database.md)** — PostgreSQL, migration.

## Phạm vi chỉnh sửa

- Code chính: `services/core-api/finance/` (hoặc app tương ứng) và `services/core-api/coresite/settings.py`, `urls.py`.

## Quy tắc cứng

- Mọi thay đổi schema: **`makemigrations`**, không sửa migration đã chạy production.
- **Không** thêm Gemini / Google Generative SDK vào Core; LLM chỉ ở `services/ai-nlp-service`.
- Giữ tương thích API client hiện có: prefix `/api/`, auth **Token** DRF.
- Endpoint **`GET /api/ai/finance-context/`** là snapshot cho AI — chỉ expose field cần thiết cho prompt, tránh leak dữ liệu nhạy cảm không cần thiết.

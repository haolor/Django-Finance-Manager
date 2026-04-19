# Cấu trúc project — Finance Microservices

Mô tả **cây thư mục** và **quy tắc đặt file** để code gen và refactor không phá vỡ ranh giới Core vs AI.

---

## 1. Gốc repo `finance-microservices/`

```
finance-microservices/
  README.md                 # Tầm nhìn, chạy Docker/local, mapping endpoint
  AGENTS.md                 # Hướng dẫn agent & developer
  .env.example              # Gợi ý biến (GemINI, DB, CORE_API_BASE_URL, …)
  .gitignore
  .claude/
    agents/                 # Gợi ý vai trò: backend, frontend, AI
    commands/               # Lệnh review, deploy, …
    rules/                  # Quy tắc kỹ thuật (system-design, api, fe, be, …)
  .cursor/
    rules/                  # Rule ngắn cho Cursor IDE
  infra/
    docker-compose.yml      # PostgreSQL + core-api + ai-nlp-service
  services/
    core-api/               # Django Core — xem mục 2
    ai-nlp-service/         # FastAPI AI — xem mục 3
```

---

## 2. Core API — `services/core-api/`

```
core-api/
  manage.py
  requirements.txt
  Dockerfile
  coresite/                 # Django project: settings, root urls, wsgi
    settings.py
    urls.py
  finance/                  # App nghiệp vụ chính (tên có thể khác nếu đổi trong code)
    models.py
    serializers.py
    views.py / viewsets.py
    urls.py
    permissions.py
    migrations/
```

**Quy tắc**

- Logic nghiệp vụ tài chính (tính toán ngân sách, rule category, …) nằm trong **app Django** hoặc module con của app — **không** nhét vào AI service.
- **Không** thêm client Gemini vào Core.

---

## 3. AI / NLP — `services/ai-nlp-service/`

```
ai-nlp-service/
  requirements.txt
  Dockerfile
  app/
    main.py                 # FastAPI app, routers, lifespan
    config.py               # Pydantic Settings / env
    core_client.py          # httpx gọi Core — token user
    gemini_client.py        # Gemini API
    nlp_service.py          # Parse text → payload Core
```

**Quy tắc**

- **Không** đặt business logic tài chính “đích danh” (persist rules) ngoài orchestration + LLM; mọi ghi DB qua **Core API**.
- Endpoint công khai version trong path: **`/v1/...`**.

---

## 4. Frontend (repo có thể tách)

Không bắt buộc nằm trong `finance-microservices/`. Khi có, cấu trúc gợi ý nằm trong [frontend-conventions.md](frontend-conventions.md) (`src/features`, `src/shared/api`, …).

---

## 5. Liên kết

- Kiến trúc logic: [system-design.md](system-design.md)
- Quy ước BE/FE: [backend-conventions.md](backend-conventions.md), [frontend-conventions.md](frontend-conventions.md)

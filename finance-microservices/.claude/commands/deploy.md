# Command: deploy

1. Build images: `docker compose -f infra/docker-compose.yml build`.
2. Set env production: `DJANGO_SECRET_KEY`, `POSTGRES_*`, `DEBUG=False`, `GEMINI_API_KEY`.
3. Chạy migrate: Core container đã chạy `migrate` ở CMD dev; production nên tách job migrate một lần trước rolling update.
4. Reverse proxy: TLS termination, upstream `core-api:8000` và `ai-nlp:8000`.
5. Health: Core `GET /api/`, AI `GET /health`.

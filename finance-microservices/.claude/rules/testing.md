# Testing

## Core

- `python manage.py test` hoặc `pytest` nếu thêm cấu hình.
- Test ViewSets: auth, tạo transaction, `finance-context` trả JSON đúng shape.

## AI service

- `httpx` mock Core responses; test FastAPI routes không gọi Gemini thật (mock `gemini_client`).
- Integration: chạy Core + DB test container, AI gọi Core thật (optional CI job).

## Frontend

- Vitest/React Testing Library cho component; E2E Playwright nếu có pipeline.

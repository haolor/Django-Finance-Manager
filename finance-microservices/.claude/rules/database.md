# Database

- **Engine:** PostgreSQL.
- **Owner:** chỉ Core API kết nối ORM; migrations chạy từ `services/core-api` (`manage.py migrate`).
- **AI service:** không có migration; không import model Django.
- Biến môi trường: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.

Khi tách DB theo service sau này: giữ schema migration riêng và chiến lược sync read-model (outbox/event) — ghi trong ADR riêng.

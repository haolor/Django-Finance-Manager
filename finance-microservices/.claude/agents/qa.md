# Agent: QA

- Kiểm tra regression: đăng ký/đăng nhập, tạo giao dịch thủ công, parse NLP qua AI, chat có trả lời khi có `GEMINI_API_KEY`.
- So sánh response shape với monolith cho các route Core giữ nguyên.
- Docker: `docker compose up` — Core healthy sau migrate, AI `/health` 200.

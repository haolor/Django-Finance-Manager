# Clean code

- Hàm ngắn, tên rõ (tiếng Anh cho code, tiếng Việt cho message user nếu product yêu cầu).
- Tránh duplicate logic giữa Core và AI — context tài chính chỉ build một nơi trên Core (`finance_context.py`).
- SOLID: AI service phụ thuộc Core qua `CoreClient`, không import Django.

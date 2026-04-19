# Security

- Không commit `.env`, API key Gemini, `DJANGO_SECRET_KEY`, mật khẩu DB.
- Production: `DEBUG=False`, `ALLOWED_HOSTS` cụ thể, HTTPS, rotate token khi cần.
- Gemini key chỉ trên AI service env; Core không cần `GEMINI_*`.
- Rate limit API (Traefik/nginx hoặc middleware) trước khi expose public.
- OCR/upload: giữ giới hạn kích thước file như Core hiện có.

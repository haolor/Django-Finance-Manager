# Error handling

- Core: dùng `Response` + HTTP status chuẩn DRF; không nuốt lỗi validation.
- AI: `HTTPException` với status 502 khi Core lỗi; 503 khi thiếu `GEMINI_API_KEY`; không leak stack trace ra client production.
- Gemini: fallback predictions qua Core `/api/ai/predictions/` khi parse JSON hoặc HTTP lỗi.

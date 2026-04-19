# Command: fix-issue

1. Tái hiện lỗi (curl hoặc Swagger `/docs` trên AI).
2. Xác định service: Core (4xx/5xx từ `/api/`) hay AI (502 thường là Core down hoặc sai URL).
3. Log: `docker compose logs core-api ai-nlp`.
4. Sửa tối thiểu; thêm test nếu có harness.
5. Cập nhật `.claude/rules/` nếu quy ước thay đổi.

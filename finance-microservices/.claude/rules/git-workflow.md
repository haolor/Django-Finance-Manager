# Git workflow

- Branch ngắn: `feature/…`, `fix/…`.
- PR nhỏ, mô tả rõ Core vs AI vs infra.
- Trước khi merge: `manage.py check`, không để secret trong diff.
- Tag release: `v1.x.x` — ghi changelog endpoint breaking (ví dụ đổi URL chatbot).

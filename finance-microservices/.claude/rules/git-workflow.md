# Git workflow

## 1. Nhánh

- `main` — luôn deployable.
- `feature/<scope>-<short>` — ví dụ `feature/auth-login`, `feature/tx-summary-endpoint`.
- `fix/<scope>-<short>` — ví dụ `fix/gateway-cors`.
- `chore/<...>` — config, docs, dependency bump.

## 2. Conventional Commits

```
<type>(<scope>): <subject>

[body]

[footer]
```

| type | dùng khi |
|------|----------|
| `feat` | Tính năng mới |
| `fix` | Sửa bug |
| `refactor` | Đổi cấu trúc, không đổi behavior |
| `chore` | Build, deps, config |
| `docs` | Tài liệu |
| `test` | Thêm/sửa test |
| `perf` | Tối ưu hiệu năng |

scope gợi ý: `auth`, `transaction`, `budget`, `notification`, `ai`, `gateway`, `eureka`, `config`, `infra`, `docs`.

Ví dụ:

```
feat(transaction): add summary endpoint by category
fix(gateway): forward Authorization header when X-User-Id present
chore(infra): bump Spring Boot to 3.3.6
```

## 3. PR

- PR nhỏ, một mục đích. Mô tả ngắn: vấn đề, hướng giải, ảnh chụp/curl response nếu áp dụng.
- Liệt kê service bị ảnh hưởng (≤ 2 service / PR là lý tưởng).
- Yêu cầu reviewer khác bounded context khi PR cross-service.

## 4. Trước khi merge

- `mvn -DskipTests clean verify` pass cho service đụng tới.
- Chạy migration mới trên Postgres test trước khi merge.
- Không leak secret trong diff (CI scan + manual review).

## 5. Tag release

- `v1.x.y` SemVer.
- Changelog ghi rõ:
  - Service nào tăng version major.
  - Migration mới (Flyway) cần coi.
  - Breaking change endpoint (nếu có) — có hướng dẫn migration.

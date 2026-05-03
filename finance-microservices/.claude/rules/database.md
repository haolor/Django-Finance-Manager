# Database — PostgreSQL per service + Flyway

## 1. Engine

- **PostgreSQL 16** (alpine image trong Docker).

## 2. Database-per-service

| Service | DB | Port host | Volume |
|---------|----|-----------|--------|
| auth-service | `auth_db` | 5433 | `finance_pg_auth` |
| transaction-service | `transaction_db` | 5434 | `finance_pg_tx` |
| budget-service | `budget_db` | 5435 | `finance_pg_budget` |
| notification-service | `notification_db` | 5436 | `finance_pg_notif` |

`ai-service` **không** có DB.

## 3. Quy tắc cứng

1. **Không** `@ManyToOne` / FK cứng giữa entity của hai service. Lưu **ID rời** (`Long userId`, `Long categoryId`, …).
2. Khi cần dữ liệu chéo → **Feign** tới REST của service kia.
3. Không service nào kết nối tới DB của service khác (kể cả read-only).

## 4. Migration — Flyway

- Đường dẫn: `src/main/resources/db/migration/V{n}__name.sql`.
- `V1__init_<service>.sql` đã có sẵn ở `auth-service`, `transaction-service`, `budget-service`, `notification-service`.
- Khi đổi schema:
  1. Tạo file mới `V{n+1}__describe_change.sql`.
  2. **Không** sửa file đã merge production.
  3. Test bằng Testcontainers: `docker run` PostgreSQL tạm và chạy Flyway.
- `spring.jpa.hibernate.ddl-auto: validate` để Hibernate không tự tạo bảng.

## 5. Biến môi trường

Mỗi service có riêng (xem `application.yml` từng module):

```
POSTGRES_<SVC>_HOST     # Trong docker-compose: postgres-<service>
POSTGRES_<SVC>_PORT     # Trong container: 5432; host: 5433-5436
POSTGRES_<SVC>_DB
POSTGRES_<SVC>_USER
POSTGRES_<SVC>_PASSWORD
```

## 6. JSON column

PostgreSQL `JSONB` được dùng cho `user_preferences.report_categories`, `dashboard_widgets`. Trong entity:

```java
@JdbcTypeCode(SqlTypes.JSON)
@Column(name = "report_categories", columnDefinition = "jsonb")
private List<Long> reportCategories = new ArrayList<>();
```

SQL Flyway:

```sql
report_categories JSONB NOT NULL DEFAULT '[]'::jsonb
```

## 7. Index

Đặt cả ở entity (`@Table(indexes = ...)`) **và** trong SQL Flyway. Ưu tiên đặt theo pattern truy vấn thực tế:

- `idx_tx_user_date (user_id, transaction_date)`
- `idx_notif_user_read (user_id, is_read)`

## 8. Backup / Restore (production gợi ý)

- `pg_dump` mỗi DB riêng theo lịch.
- Restore từng DB không ảnh hưởng service khác (lợi ích tách).

## 9. Tương lai

- Read replica cho `transaction-service` khi đọc nặng (query thống kê).
- Outbox table trong `transaction-service` để publish event tới message broker.

# transaction-service

Microservice quản lý **Category**, **Transaction**, **SpendingPattern**.

- Port: `8082`.
- Database: `transaction_db` (PostgreSQL).
- Lưu `userId` (Long) rời, **không** FK chéo sang `auth-service`.

## Endpoint

### Categories (public read)

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/api/categories` | List |
| GET | `/api/categories/{id}` | Detail |
| POST | `/api/categories` | Create |
| PUT | `/api/categories/{id}` | Update |
| DELETE | `/api/categories/{id}` | Delete |

### Transactions (yêu cầu Bearer JWT)

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/api/transactions?categoryId=&fromDate=YYYY-MM-DD&toDate=YYYY-MM-DD&page=0&size=20` | Phân trang Spring Data |
| GET | `/api/transactions/{id}` | Chi tiết của user hiện tại |
| POST | `/api/transactions` | Tạo |
| PUT | `/api/transactions/{id}` | Cập nhật |
| DELETE | `/api/transactions/{id}` | Xóa |

## Auth

- Tin tưởng header `X-User-Id`/`X-Username` do `api-gateway` inject sau khi verify JWT.
- Cũng tự verify `Authorization: Bearer <jwt>` khi được gọi nội bộ (zero-trust) — cùng `JWT_SECRET`.

## Biến môi trường

| Biến | Mặc định |
|------|----------|
| `POSTGRES_TX_HOST` | `localhost` |
| `POSTGRES_TX_PORT` | `5434` |
| `POSTGRES_TX_DB` | `transaction_db` |
| `POSTGRES_TX_USER` / `POSTGRES_TX_PASSWORD` | `postgres` / `postgres` |
| `JWT_SECRET` | dev |
| `EUREKA_URL` | `http://localhost:8761/eureka/` |

## Chạy local

```bash
mvn -pl services/transaction-service -am spring-boot:run
```

## TODO

- Endpoint thống kê: `/api/transactions/summary` (theo tháng), `/api/transactions/by-category`.
- Đồng bộ `SpendingPattern` (job/event sau mỗi giao dịch).
- Endpoint `GET /api/ai/finance-context/` (dữ liệu cho ai-service).

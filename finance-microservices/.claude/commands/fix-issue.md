# Command: fix-issue

## 1. Tái hiện

- Lấy `Authorization: Bearer <jwt>` của user đang gặp lỗi.
- Reproduce qua `curl` hoặc Postman, hit thẳng **gateway** (`http://localhost:8080`):

```bash
curl -i http://localhost:8080/api/transactions -H "Authorization: Bearer $TOKEN"
```

## 2. Xác định service bị lỗi

| Dấu hiệu | Nghi ngờ |
|----------|----------|
| 401 ngay từ gateway | JWT sai/hết hạn, hoặc `JWT_SECRET` lệch |
| 502/503 | Service downstream chết / chưa register Eureka |
| 500 + ProblemDetail | Bug trong business service |
| Eureka dashboard thiếu service | Service crash hoặc `EUREKA_URL` sai |
| Config Server 404 | `bootstrap.yml` thiếu `spring.config.import` hoặc `CONFIG_SERVER_URL` sai |

## 3. Log

```bash
# Toàn bộ
docker compose logs -f

# Một service
docker compose logs -f transaction-service

# Kết hợp
docker compose logs -f api-gateway transaction-service
```

Filter theo level:

```bash
docker compose logs api-gateway | rg "ERROR|WARN"
```

## 4. Kiểm tra Eureka

```bash
curl http://localhost:8761/eureka/apps -H "Accept: application/json" | jq '.applications.application[] | .name'
```

## 5. Kiểm tra Config Server

```bash
curl http://localhost:8888/auth-service/default | jq
curl http://localhost:8888/api-gateway/default | jq
```

## 6. Kiểm tra DB

```bash
docker exec -it $(docker compose ps -q postgres-transaction) \
  psql -U postgres -d transaction_db -c "SELECT * FROM flyway_schema_history;"
```

## 7. Sửa & test

1. Sửa code (giữ thay đổi tối thiểu).
2. Thêm test (unit / IT) tái hiện bug và xác nhận fix.
3. Build lại service đụng tới: `mvn -pl services/transaction-service -am package`.
4. Build image và restart: `docker compose up -d --build transaction-service`.
5. Verify lại bằng curl.

## 8. Cập nhật tài liệu

- Nếu thay đổi API contract → cập nhật `api-conventions.md` + `<service>/README.md`.
- Nếu thêm biến môi trường → cập nhật `.env.example` + README + Dockerfile/compose.
- Nếu đổi quy ước → cập nhật `.claude/rules/`.

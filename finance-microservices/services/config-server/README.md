# config-server

**Spring Cloud Config Server** chạy ở port `8888`, profile `native`, đọc cấu hình tập trung từ:

- `${CONFIG_NATIVE_SEARCH_LOCATIONS}` — mặc định `file:./config-repo,classpath:/config-repo`.
- Khi chạy bằng `docker compose`, mount `infra/config-repo` vào `/app/config-repo` và đặt `CONFIG_NATIVE_SEARCH_LOCATIONS=file:/app/config-repo`.

## Endpoint kiểm tra

```bash
curl http://localhost:8888/auth-service/default
curl http://localhost:8888/transaction-service/default
```

## Chạy local

```bash
mvn -pl services/config-server -am spring-boot:run
```

# api-gateway

**Spring Cloud Gateway** (reactive) chạy ở port `8080`. Là điểm vào duy nhất của hệ thống.

## Routing

| Path predicate | Đích |
|----------------|------|
| `/api/auth/**` | `auth-service` |
| `/api/categories/**`, `/api/transactions/**` | `transaction-service` |
| `/api/budgets/**` | `budget-service` |
| `/api/notifications/**` | `notification-service` |
| `/v1/**` | `ai-service` |

## JWT GlobalFilter

`com.finance.gateway.filter.JwtAuthenticationFilter` (order `-100`):

1. Bypass các path public: `/api/auth/register`, `/api/auth/login`, `/actuator/health`, `/actuator/info`.
2. Yêu cầu header `Authorization: Bearer <jwt>`.
3. Verify HS256 với `finance.security.jwt.secret`.
4. Inject header `X-User-Id` (từ claim `sub`) và `X-Username` cho downstream service.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|------|----------|---------|
| `JWT_SECRET` | `please-change-me-...` | Chia sẻ với mọi service |
| `EUREKA_URL` | `http://localhost:8761/eureka/` | Eureka server |
| `CONFIG_SERVER_URL` | `http://localhost:8888` | Config Server |
| `GATEWAY_ALLOWED_ORIGINS` | `*` | CORS origin pattern |

## Chạy local

```bash
mvn -pl services/api-gateway -am spring-boot:run
```

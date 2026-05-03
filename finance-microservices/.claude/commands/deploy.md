# Command: deploy

## 1. Build artifacts

```bash
cd finance-microservices
mvn -DskipTests clean package
```

Artifacts ở `services/<svc>/target/<svc>-1.0.0-SNAPSHOT.jar`.

## 2. Build Docker images

Mỗi service có Dockerfile multi-stage (Maven build → JRE run).

```bash
cd finance-microservices/infra
docker compose build
```

Hoặc build từng service:

```bash
docker compose build auth-service transaction-service api-gateway
```

## 3. Cấu hình production

Đặt biến môi trường (qua secret manager / `.env` không commit):

```env
JWT_SECRET=<random 64+ chars>
POSTGRES_PASSWORD=<strong password>

# AI service
VERTEX_PROJECT_ID=<gcp project>
VERTEX_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp-credentials.json

# notification-service SMTP
MAIL_HOST=...
MAIL_USERNAME=...
MAIL_PASSWORD=...

# Gateway CORS
GATEWAY_ALLOWED_ORIGINS=https://finance.example.com
```

## 4. Thứ tự khởi động (production)

1. PostgreSQL (4 instance riêng) — chờ healthy.
2. `discovery-server` (Eureka).
3. `config-server`.
4. `api-gateway`, các business service, `ai-service` — đăng ký Eureka, fetch config.

`docker compose up -d` đã có `depends_on` + `service_healthy` cho dev. Production K8s: dùng `readinessProbe` (`/actuator/health/readiness`).

## 5. Migration Flyway

- Chạy tự động khi service boot (`spring.flyway.enabled: true`).
- Production: tách job migrate trước khi rolling update để tránh nhiều instance cùng chạy migration:

```bash
docker run --rm \
  -e POSTGRES_TX_HOST=... \
  finance/transaction-service:latest \
  java -jar /app/app.jar --spring.profiles.active=migration --spring.main.web-application-type=none
```

(Hoặc tách Flyway CLI image — tùy chiến lược).

## 6. Reverse proxy + TLS

- Đặt NGINX/Traefik/Cloud LB phía trước `api-gateway`.
- TLS termination ở proxy. `api-gateway` listen HTTP nội bộ.
- Allowlist origin + rate limit ở proxy.

## 7. Health check

| Service | Endpoint |
|---------|----------|
| Gateway | `GET /actuator/health` |
| Eureka | `GET /actuator/health` |
| Config | `GET /actuator/health` |
| Business services | `GET /actuator/health` (qua gateway: `/{path}/actuator/health` chỉ public nếu được route) |

## 8. Rollback

- Nếu service mới crash: `docker compose up -d --no-deps <service>` với image tag cũ.
- Migration không tự rollback — cần script DOWN nếu cần thiết (Flyway không hỗ trợ undo trừ Pro).

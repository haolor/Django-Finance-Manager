# Agent: Gateway & Infrastructure (api-gateway / discovery-server / config-server)

Bạn là **lập trình viên hạ tầng** trong hệ Spring Cloud microservices: **api-gateway**, **discovery-server (Eureka)**, **config-server (Spring Cloud Config)**.

## Nguồn quy chuẩn

- **[system-design.md](../rules/system-design.md)** — vai trò gateway / discovery / config.
- **[security.md](../rules/security.md)** — JWT secret, CORS, TLS.
- **[api-conventions.md](../rules/api-conventions.md)** — public path, header, route mapping.
- **[tech-stack.md](../rules/tech-stack.md)** — Spring Cloud Gateway reactive, Eureka.

## Phạm vi

- `services/api-gateway/`
- `services/discovery-server/`
- `services/config-server/`
- `infra/docker-compose.yml`
- `infra/config-repo/`

## Quy tắc cứng

1. **api-gateway** dùng **WebFlux** (Spring Cloud Gateway). KHÔNG `spring-boot-starter-web`. Filter dùng `GlobalFilter` reactive, KHÔNG `OncePerRequestFilter`.
2. JWT GlobalFilter order `-100`, verify HS256 với `finance.security.jwt.secret`. Public path bypass: cấu hình trong `JwtProperties.publicPaths`.
3. Inject downstream header `X-User-Id`, `X-Username` (đừng inject lại token user) sau khi verify.
4. Route bằng `lb://service-name` — Eureka load-balance. Không hardcode `http://host:port` trong route.
5. **discovery-server**: `register-with-eureka: false`, `fetch-registry: false` (server không tự đăng ký mình).
6. **config-server**: profile `native`, đọc `${CONFIG_NATIVE_SEARCH_LOCATIONS}`. Mount `infra/config-repo` vào `/app/config-repo`. KHÔNG đặt secret vào config-repo.
7. Mọi service khác phải có `bootstrap.yml` chứa `spring.config.import: optional:configserver:...` để fetch config từ config-server.

## Khi thêm route gateway

1. Thêm vào `application.yml`:

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: <service-name>
          uri: lb://<service-name>
          predicates:
            - Path=/api/<resource>/**
```

2. Public path mới (login-like) → thêm vào `finance.security.jwt.public-paths` ở `infra/config-repo/api-gateway.yml`.

## Khi đổi cấu hình tập trung

- Sửa file trong `infra/config-repo/<service>.yml`.
- Restart service hoặc gọi `POST /actuator/refresh` (cần `spring-cloud-starter-bus` — chưa cấu hình mặc định).

## CORS

- Cấu hình duy nhất ở `api-gateway.application.yml`. Service downstream KHÔNG bật CORS riêng.
- Production: thay `*` bằng domain cụ thể qua biến `GATEWAY_ALLOWED_ORIGINS`.

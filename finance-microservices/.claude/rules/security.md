# Security

## 1. Bí mật & quản lý cấu hình

- **Không** commit: `.env`, `JWT_SECRET`, `GOOGLE_APPLICATION_CREDENTIALS` (file JSON), mật khẩu DB, SMTP password.
- File `.gitignore` đã chặn `.env`, `gcp-credentials*.json`, `*.iml`, `target/`.
- Production: dùng **secret manager** (HashiCorp Vault, GCP Secret Manager, AWS Secrets Manager) thay vì env file.
- Spring Cloud Config Server có thể tích hợp Vault qua `spring-cloud-config-server-vault` (chưa cấu hình mặc định).

## 2. JWT

- Thuật toán: **HS256**, secret tối thiểu **32 ký tự** (256-bit). Khuyến nghị 64+ ký tự ngẫu nhiên.
- TTL access token: **12 giờ** mặc định (`finance.security.jwt.access-token-ttl: PT12H`). Có thể giảm xuống 1h + thêm refresh-token sau.
- Tất cả service phải dùng **cùng** `JWT_SECRET`. Đặt qua biến môi trường, KHÔNG nhúng vào `application.yml` mặc định.
- Nâng cấp tương lai: chuyển sang **RS256** (auth-service ký bằng private key, các service verify bằng public key qua JWKS endpoint) để loại bỏ secret chung.

## 3. Gateway

- `JwtAuthenticationFilter` order `-100` (chạy sớm nhất).
- Public path cấu hình tập trung trong `finance.security.jwt.public-paths`.
- CORS: cấu hình `GATEWAY_ALLOWED_ORIGINS` trong env (mặc định `*` cho dev — production phải fix domain cụ thể).
- Rate limit: thêm `RequestRateLimiter` filter (Redis) khi production.

## 4. Service downstream

- Tự verify JWT — không tin tưởng riêng `X-User-Id` từ gateway. Triển khai **defense in depth** (mạng nội bộ có thể bị compromise).
- `SecurityConfig` STATELESS, không tạo HTTP session.

## 5. Mật khẩu

- Hash bằng **BCrypt** (`BCryptPasswordEncoder`). Không bao giờ lưu plain text.
- Validate độ dài ≥ 8 trên DTO; có thể nâng lên 12 cho production.

## 6. AI / Gemini

- `GEMINI_API_KEY` / `GOOGLE_APPLICATION_CREDENTIALS` chỉ trên `ai-service`. Service khác **không** có biến này.
- Frontend tuyệt đối không có khoá LLM (`VITE_GEMINI_*` cấm).
- Khi log: KHÔNG log prompt đầy đủ chứa PII (tên, số tiền lớn, …) trong production. Mask trước khi log.

## 7. Giới hạn input

- Body upload (OCR sau này): `spring.servlet.multipart.max-file-size: 10MB`.
- Validation `@Size` trên text input để tránh prompt-injection / DoS.

## 8. CORS

- Dev: `*` cho thuận tiện.
- Prod: chỉ allow `https://finance.example.com`. Cấu hình ở `api-gateway` (vì là entry point duy nhất).

## 9. TLS

- Production: TLS terminator (NGINX, Traefik, hoặc cloud LB) phía trước gateway. Gateway listen HTTP nội bộ.
- Internal mTLS giữa service: tương lai (Istio / Linkerd / Spring Cloud Gateway client SSL).

## 10. Audit

- Log every login (success + fail) ở `auth-service`.
- Tương lai: ghi audit table riêng (ai làm gì, IP) trong `auth-service` hoặc service log tập trung.

## 11. Phụ thuộc & vulnerability

- Theo dõi `mvn versions:display-dependency-updates` định kỳ.
- Bật GitHub Dependabot / Snyk cho repo.
- Không downgrade Spring Boot xuống version ngoài hỗ trợ.

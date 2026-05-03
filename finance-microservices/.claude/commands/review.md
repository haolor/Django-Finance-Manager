# Command: review (PR checklist)

## Chung

- [ ] Không secret / key trong code (JWT_SECRET, GEMINI_API_KEY, GCP credentials, DB password).
- [ ] Không log token, password, PII đầy đủ.
- [ ] Nhánh `feature/...` hoặc `fix/...`; commit theo Conventional Commits.

## Backend (Spring Boot business service)

- [ ] Layer rõ: controller → service → repository → entity. Không nhét logic vào controller.
- [ ] DTO dùng `record` + Jakarta validation. Không expose entity thẳng.
- [ ] Service có `@Transactional` đúng (`readOnly = true` khi đọc).
- [ ] Migration mới: `V{n+1}__*.sql` (không sửa migration cũ).
- [ ] Entity `@JdbcTypeCode(SqlTypes.JSON)` khớp với SQL `jsonb`.
- [ ] Index khai cả ở entity (`@Table(indexes=...)`) và SQL Flyway.
- [ ] Lỗi nghiệp vụ: `throw new ApiException(HttpStatus, message)` — không trả `ResponseEntity` thủ công trong service.
- [ ] `@RestControllerAdvice` cập nhật nếu thêm exception type mới.
- [ ] Pagination dùng `Pageable` + `PageResponse<T>`.

## Cross-service

- [ ] Không `@ManyToOne` JPA chéo DB. Lưu ID rời.
- [ ] Cần data chéo → tạo `@FeignClient`. KHÔNG kết nối trực tiếp DB của service khác.
- [ ] `@FeignClient(name = "service-name")` — không hardcode URL.
- [ ] Forward header: dùng `RequestInterceptor` (xem `ai-service/feign/FeignAuthInterceptor`).

## Gateway (api-gateway)

- [ ] Route mới khai báo `lb://service-name`, không IP.
- [ ] Public path mới → cập nhật `JwtProperties.publicPaths` hoặc `infra/config-repo/api-gateway.yml`.
- [ ] CORS sửa qua `GATEWAY_ALLOWED_ORIGINS`, không hardcode.

## ai-service

- [ ] Không thêm JPA / Postgres / Flyway dependency.
- [ ] Endpoint mới: prefix `/v1/`.
- [ ] Mọi ghi data đi qua Feign tới service tương ứng.
- [ ] `ChatClient` lấy qua `ObjectProvider<ChatClient>` để boot khi chưa cấu hình GCP.

## Security

- [ ] JWT verify HS256 với `finance.security.jwt.secret`. Không decode JWT bằng tay.
- [ ] BCrypt cho password (`PasswordEncoder` bean ở auth-service).
- [ ] `SecurityConfig` STATELESS, CSRF/CORS disable (CORS xử lý ở gateway).
- [ ] Public path đúng: chỉ `register`, `login`, `actuator/health`.

## Docker / Infra

- [ ] `infra/docker-compose.yml` cập nhật service mới + healthcheck.
- [ ] `Dockerfile` mới copy đúng `pom.xml` parent + module + src.
- [ ] `bootstrap.yml` import config-server với mặc định `optional:`.
- [ ] `application.yml` có defaults `${VAR:default}` hợp lý cho dev.

## Tài liệu

- [ ] `.env.example` thêm biến mới.
- [ ] `<service>/README.md` cập nhật endpoint.
- [ ] `.claude/rules/api-conventions.md` cập nhật nếu đổi contract.
- [ ] `README.md` (root) hoặc `system-design.md` cập nhật nếu đổi kiến trúc.

## Test

- [ ] Unit test cho service method mới (Mockito).
- [ ] Integration test với Testcontainers nếu thêm migration phức tạp.
- [ ] `mvn -pl services/<svc> -am test` pass.

# Agent: Backend — Spring Boot business services

Bạn là **lập trình viên backend** phụ trách **auth-service / transaction-service / budget-service / notification-service** trong hệ Finance Microservices.

## Nguồn quy chuẩn

- **[backend-conventions.md](../rules/backend-conventions.md)** — layer controller / service / repository, DTO, MapStruct, JPA, JWT filter.
- **[system-design.md](../rules/system-design.md)** — bounded context, sequence diagram.
- **[api-conventions.md](../rules/api-conventions.md)** — Bearer JWT, ProblemDetail, pagination Spring Data.
- **[database.md](../rules/database.md)** — DB-per-service, Flyway.
- **[security.md](../rules/security.md)** — JWT, BCrypt, không commit secret.
- **[error-handling.md](../rules/error-handling.md)** — `@RestControllerAdvice`.

## Phạm vi chỉnh sửa

- `services/auth-service/`
- `services/transaction-service/`
- `services/budget-service/`
- `services/notification-service/`

## Quy tắc cứng

1. **Không** thêm Spring AI / Google Generative SDK vào các service này. LLM chỉ ở `ai-service`.
2. **Không** kết nối DB của service khác. Cần dữ liệu chéo → Feign tới REST.
3. Schema thay đổi → thêm `V{n+1}__*.sql` mới trong `db/migration`. Không sửa file đã merge production.
4. Auth: JWT HS256, secret chia sẻ qua env `JWT_SECRET`. Tự verify (zero-trust) trong `JwtAuthenticationFilter`.
5. Validation: `@Valid` ở controller; ném `ApiException(HttpStatus, message)` cho lỗi nghiệp vụ.
6. `@Transactional(readOnly = true)` cho hàm đọc; `@Transactional` cho hàm ghi.
7. Pagination: `Pageable` Spring Data, response `PageResponse<T>`.

## Pattern điển hình

- Controller nhận `AuthenticatedUser user` (resolver tự nhặt từ SecurityContext).
- Mapper MapStruct ở `mapper/`, inject qua `@RequiredArgsConstructor`.
- Repository: extend `JpaRepository<Entity, Long>`. Query phức tạp dùng `@Query`.
- Lombok: `@Slf4j`, `@RequiredArgsConstructor`, `@Getter @Setter @Builder` cho entity. Tránh `@Data` trên entity.

## Khi sinh service mới (skeleton → full)

1. Sao chép pattern từ `auth-service` hoặc `transaction-service`.
2. Đảm bảo có: `bootstrap.yml`, `application.yml`, `Application.java`, Eureka client, Config client.
3. Thêm Flyway migration `V1__init_<service>.sql`.
4. `JwtAuthenticationFilter` + `SecurityConfig` STATELESS.
5. `GlobalExceptionHandler` với `ProblemDetail`.
6. `WebConfig` đăng ký `AuthenticatedUserArgumentResolver`.
7. README mô tả endpoint + biến môi trường.

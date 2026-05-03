# Quy ước Backend — Spring Boot / Spring Cloud

Tài liệu chuẩn hóa **cấu trúc layer**, **DTO**, **persistence**, **REST**, **inter-service** cho mọi service trong repo.

---

## 1. Layer chuẩn

```
controller (HTTP)  →  service (business + @Transactional)  →  repository (Spring Data JPA)  →  entity (@Entity)
                       ↑
                       mapper (MapStruct) chuyển entity ↔ DTO
```

- **Controller**: thin, không chứa business logic. Nhận DTO `@Valid`, trả DTO/`PageResponse`. Không inject `EntityManager` hay `Repository` trực tiếp.
- **Service**: nơi đặt `@Transactional`. Method ghi: `@Transactional`. Method đọc: `@Transactional(readOnly = true)`.
- **Repository**: extend `JpaRepository<Entity, Long>`. Query phức tạp dùng `@Query` JPQL (xem `TransactionRepository`).
- **Entity**: `@Entity`, `@Table`, `@Column` rõ ràng. ID `Long` + `GenerationType.IDENTITY`. Lombok `@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder`.

---

## 2. DTO

- Dùng **Java `record`** cho request/response (immutable, brief).
- Validation Jakarta:
  - `@NotBlank`, `@NotNull`, `@Size`, `@Email`, `@DecimalMin`, `@PastOrPresent`, `@Pattern`.
- `Pageable` + `PageResponse<T>` cho list endpoint.

```java
public record TransactionDto(
    Long id,
    Long userId,
    Long categoryId,
    @NotNull @DecimalMin("0.01") BigDecimal amount,
    String description,
    @NotNull @PastOrPresent LocalDate transactionDate,
    String originalNlpInput,
    Instant createdAt,
    Instant updatedAt
) {}
```

---

## 3. MapStruct

- Annotation processor đã cấu hình ở parent `pom.xml` (Lombok binding bao gồm).
- Interface `@Mapper(componentModel = SPRING)`; tự động được Spring inject.
- Đặt ở `mapper/` package; mỗi service một mapper trở lên tuỳ scope.

---

## 4. Persistence & Flyway

- `spring.jpa.hibernate.ddl-auto: validate` — Flyway mới được phép tạo bảng.
- Migration tại `src/main/resources/db/migration/V{n}__name.sql`. Chạy tăng dần.
- **Không** sửa migration đã merge production. Tạo file V{n+1} mới.
- JSON column: `@JdbcTypeCode(SqlTypes.JSON)` + `columnDefinition = "jsonb"`. Khai báo `JSONB NOT NULL DEFAULT '[]'::jsonb` trong SQL.
- Index trong entity: `@Table(indexes = {@Index(...)})` đồng thời khai trong SQL Flyway.

---

## 5. Auth context trong controller

Mọi service business dùng pattern sau để lấy user hiện tại trong controller:

```java
public record AuthenticatedUser(Long id, String username) {}

@GetMapping
public PageResponse<TransactionDto> list(AuthenticatedUser user, Pageable pageable) {
    return service.search(user.id(), ..., pageable);
}
```

Resolver tự nhặt từ `SecurityContextHolder` sau khi `JwtAuthenticationFilter` chạy.

---

## 6. JWT verify (mỗi service)

- Cấu hình `finance.security.jwt.secret` (cùng giá trị toàn hệ thống — `JWT_SECRET` env).
- `JwtAuthenticationFilter extends OncePerRequestFilter`:
  1. Ưu tiên `X-User-Id` / `X-Username` (gateway đã verify).
  2. Nếu không có, tự verify `Authorization: Bearer <jwt>` bằng JJWT HS256.
- `SecurityConfig`:

```java
http
  .csrf(disable)
  .cors(disable)
  .sessionManagement(STATELESS)
  .authorizeHttpRequests(a -> a
      .requestMatchers("/actuator/**").permitAll()
      .anyRequest().authenticated())
  .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
```

---

## 7. Inter-service call (Feign)

```java
@FeignClient(name = "transaction-service")
public interface TransactionClient {
    @GetMapping("/api/ai/finance-context")
    String financeContext();
}
```

- Tên service trùng `spring.application.name` (Eureka load-balance).
- Forward header bằng `RequestInterceptor` (xem `ai-service/feign/FeignAuthInterceptor`).
- Bật `@EnableFeignClients` trên `*Application.java`.

---

## 8. ai-service (đặc biệt)

- **Không** Spring Web đầy đủ với DB — không có JPA.
- `ChatClient` qua `ObjectProvider<ChatClient>` để boot được khi chưa cấu hình GCP.
- Logic NLP/parse: viết trong `service/` (chưa có), dùng Spring AI structured output (`call().entity(MyDto.class)`).

---

## 9. Phong cách Java chung

- PEP-equivalent: 4 spaces, không tab.
- `record` cho DTO; `@Builder` chỉ dùng cho entity hoặc DTO mutable phức tạp.
- Tránh field injection. Constructor injection (`@RequiredArgsConstructor` Lombok).
- `@Slf4j` cho logging (Lombok). KHÔNG `System.out.println`.
- Tránh static state. Bean Spring là singleton, dùng đúng scope.

---

## 10. Tóm tắt ranh giới

| Việc | gateway | auth | tx | budget | notif | ai |
|------|:-------:|:----:|:--:|:------:|:-----:|:--:|
| JPA + Postgres | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Phát hành JWT | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Verify JWT | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Spring AI / Gemini | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Feign tới service khác | ❌ | (không) | (sẽ có) | ✅ | ✅ | ✅ |

# Testing

## 1. Stack

- **JUnit 5** (Jupiter) — đi kèm `spring-boot-starter-test`.
- **Mockito** — mock dependency.
- **AssertJ** — assertion fluent.
- **Spring Boot Test slices**: `@WebMvcTest`, `@DataJpaTest`, `@SpringBootTest`.
- **Testcontainers** (BOM 1.20.4) — PostgreSQL container thật cho integration test.
- **MockMvc** — test controller.

## 2. Cấu trúc test

```
src/test/java/com/finance/<svc>/
  <ClassName>Tests.java     # Unit (Mockito)
  <ClassName>IT.java        # Integration (Spring Boot + Testcontainers)
```

## 3. Unit test — service

```java
@ExtendWith(MockitoExtension.class)
class AuthServiceTests {

    @Mock UserRepository userRepository;
    @Mock UserPreferencesRepository preferencesRepository;
    @Mock PasswordEncoder passwordEncoder;
    @Mock JwtService jwtService;
    @Mock UserMapper userMapper;
    @InjectMocks AuthService authService;

    @Test
    void register_should_throw_when_username_exists() {
        when(userRepository.existsByUsername("john")).thenReturn(true);
        assertThatThrownBy(() -> authService.register(new RegisterRequest("john", "j@x.com", "secret123", null, null)))
            .isInstanceOf(ApiException.class);
    }
}
```

## 4. Slice test — controller

```java
@WebMvcTest(AuthController.class)
@AutoConfigureMockMvc(addFilters = false) // bỏ JwtFilter trong slice test
class AuthControllerTests {
    @Autowired MockMvc mockMvc;
    @MockBean AuthService authService;
    // ...
}
```

## 5. Integration test — Testcontainers

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class TransactionFlowIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired TestRestTemplate rest;

    @Test
    void create_and_list_transactions() {
        // POST + GET
    }
}
```

## 6. Test cho ai-service

- Dùng `@MockBean ChatModel` (Spring AI) — không gọi Gemini thật.
- Mock `TransactionClient` Feign bằng `@MockBean`.

## 7. Test gateway

- `@SpringBootTest` với reactive `WebTestClient`.
- Tạo JWT test bằng JJWT cùng secret rồi assert `200`.

## 8. Smoke test toàn hệ thống (manual)

```bash
# Sau docker compose up:
curl http://localhost:8761/actuator/health
curl http://localhost:8888/auth-service/default
curl http://localhost:8080/actuator/health

# Đăng ký
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@x.com","password":"secret123"}'

# Đăng nhập
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}' | jq -r .token)

# Gọi protected
curl http://localhost:8080/api/auth/profile -H "Authorization: Bearer $TOKEN"
curl http://localhost:8080/api/categories
```

## 9. CI gợi ý

- Chạy `mvn -DskipITs test` (unit) ở mọi PR.
- Chạy `mvn verify` (kèm IT Testcontainers) ở nightly hoặc trước release.
- GitHub Actions workflow `.github/workflows/ci.yml` (chưa có — TODO).

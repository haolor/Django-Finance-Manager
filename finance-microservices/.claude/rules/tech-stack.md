# Tech stack — Finance Microservices (Spring Cloud)

Tổng hợp **công nghệ** và **giới hạn** từng service. Tránh lệch stack khi gen code hoặc thêm dependency.

---

## 1. Toàn bộ repo

| Hạng mục | Lựa chọn | Ghi chú |
|----------|----------|---------|
| Ngôn ngữ | **Java 21 LTS** | `--enable-preview` không bật |
| Build | **Maven** multi-module | Parent `pom.xml` ở root |
| Spring Boot | **3.3.5** | Bóc qua `spring-boot-starter-parent` |
| Spring Cloud | **2024.0.0** | BOM trong `dependencyManagement` |
| Spring AI | **1.0.0-M3** | BOM, milestone repo `repo.spring.io/milestone` |
| JJWT | **0.12.6** | `jjwt-api`, `jjwt-impl` (runtime), `jjwt-jackson` (runtime) |
| MapStruct | **1.6.3** | + `lombok-mapstruct-binding` 0.2.0 |
| Lombok | **1.18.34** | provided + annotationProcessor |
| Testcontainers | **1.20.4** | BOM |
| Container runtime | Docker 24+, Compose v2 | |

---

## 2. api-gateway

| Thành phần | Công nghệ | Ghi chú |
|-----------|-----------|---------|
| Web | Spring Cloud Gateway (reactive Netty) | KHÔNG dùng spring-boot-starter-web |
| Discovery | Eureka client | |
| Config | Spring Cloud Config client | bootstrap |
| JWT | JJWT 0.12.x | `JwtAuthenticationFilter implements GlobalFilter` |
| CORS | Spring Cloud Gateway global CORS | |

---

## 3. discovery-server

| Thành phần | Công nghệ |
|-----------|-----------|
| Eureka Server | `spring-cloud-starter-netflix-eureka-server` |
| Actuator | `spring-boot-starter-actuator` |

---

## 4. config-server

| Thành phần | Công nghệ |
|-----------|-----------|
| Config Server | `spring-cloud-config-server` |
| Profile | `native` (đọc file system: `infra/config-repo`) |

---

## 5. auth-service / transaction-service / budget-service / notification-service

| Thành phần | Công nghệ | Ghi chú |
|-----------|-----------|---------|
| Web | `spring-boot-starter-web` (MVC, Tomcat) | |
| Persistence | `spring-boot-starter-data-jpa` + Hibernate 6 | |
| DB driver | `org.postgresql:postgresql` (runtime) | |
| Migration | `flyway-core` + `flyway-database-postgresql` | `db/migration/V{n}__*.sql` |
| Security | `spring-boot-starter-security` | STATELESS, custom `JwtAuthenticationFilter` |
| Validation | `spring-boot-starter-validation` (Hibernate Validator) | |
| Discovery | `spring-cloud-starter-netflix-eureka-client` | |
| Config | `spring-cloud-starter-config` + `spring-cloud-starter-bootstrap` | |
| Inter-service | `spring-cloud-starter-openfeign` (budget, notification, ai) | |
| Mail (chỉ notification) | `spring-boot-starter-mail` | |
| JWT | JJWT 0.12.x | Verify HS256 |
| Mapper | MapStruct + Lombok binding | |
| JSON columns | Hibernate 6 `@JdbcTypeCode(SqlTypes.JSON)` | Không cần thư viện ngoài |

---

## 6. ai-service

| Thành phần | Công nghệ | Ghi chú |
|-----------|-----------|---------|
| Spring AI | `spring-ai-vertex-ai-gemini-spring-boot-starter` | Cần GCP project + ADC |
| Feign | `spring-cloud-starter-openfeign` | Forward `Authorization`, `X-User-Id`, `X-Username` |
| KHÔNG có | JPA / Postgres / Flyway | Stateless |

**Không** thêm Spring AI starter vào service khác.

---

## 7. Frontend (repo có thể tách)

| Thành phần | Công nghệ |
|-----------|-----------|
| UI | React 18+ |
| Build | Vite |
| Style | Tailwind CSS |
| HTTP | `fetch` / axios + một lớp `apiClient` duy nhất gọi gateway |

Biến môi trường:

- `VITE_API_BASE_URL` — ví dụ `http://localhost:8080` (gateway, **một** base URL).

**Không** có biến `VITE_GEMINI_API_KEY`, `VITE_JWT_SECRET`.

---

## 8. Hạ tầng & vận hành

| Thành phần | Ghi chú |
|------------|---------|
| Docker Compose | `infra/docker-compose.yml` — 4 Postgres + 8 service |
| Reverse proxy (tương lai) | TLS termination trước `api-gateway`, rate limit, IP allowlist admin |
| K8s (tương lai) | Helm chart per service; Spring Cloud Kubernetes thay Eureka nếu chuyển sang |

---

## 9. Ma trận “được phép / không được”

| Công nghệ | gateway | auth | tx | budget | notif | ai | discovery | config |
|-----------|:-------:|:----:|:--:|:------:|:-----:|:--:|:---------:|:------:|
| Spring Web (MVC) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Spring Cloud Gateway | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| JPA + Postgres | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Spring AI / Gemini | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Feign | (có thể) | (không cần) | (sẽ thêm) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Mail | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |

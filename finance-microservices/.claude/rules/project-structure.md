# Cấu trúc project — Finance Microservices

Mô tả **cây thư mục** và **quy tắc đặt file** để code gen / refactor không phá vỡ ranh giới Spring Cloud.

---

## 1. Gốc repo `finance-microservices/`

```
finance-microservices/
  pom.xml                         # Parent multi-module (Java 21, BOM SB+SC+AI)
  README.md
  AGENTS.md
  .env.example
  .gitignore
  .claude/
    rules/                        # Quy tắc kỹ thuật
    agents/                       # Vai trò agent
    commands/                     # Lệnh review/deploy/fix-issue
  .cursor/
    rules/finance-microservices.mdc
  infra/
    docker-compose.yml
    config-repo/                  # Native config files cho config-server
  services/
    config-server/
    discovery-server/
    api-gateway/
    auth-service/
    transaction-service/
    budget-service/
    notification-service/
    ai-service/
```

---

## 2. Cấu trúc chuẩn cho một business service Spring Boot

```
services/<service-name>/
  pom.xml
  Dockerfile
  README.md
  src/main/
    java/com/finance/<package>/
      <ServiceName>Application.java
      controller/                 # @RestController, mapping URL
      service/                    # Business logic, @Transactional
      repository/                 # Spring Data JPA interface
      entity/                     # @Entity (JPA)
      dto/                        # record, validation
      mapper/                     # MapStruct
      config/                     # SecurityConfig, WebConfig, ConfigurationProperties
      security/                   # AuthenticatedUser, JwtAuthenticationFilter
      exception/                  # ApiException, GlobalExceptionHandler
      feign/                      # @FeignClient + RequestInterceptor (nếu cần)
    resources/
      bootstrap.yml               # name + config-server import
      application.yml             # port, datasource, eureka
      db/migration/V{n}__*.sql    # Flyway
  src/test/
    java/com/finance/<package>/
      ...IT.java                  # Integration test (Testcontainers)
      ...Tests.java               # Unit test
```

---

## 3. Hạ tầng (config-server, discovery-server, api-gateway)

Cấu trúc tối giản, không có `entity/`, `repository/`:

```
services/<infra-service>/
  pom.xml
  Dockerfile
  README.md
  src/main/
    java/com/finance/<package>/
      <Name>Application.java
      config/                     # Tuỳ service (filter, properties)
      filter/                     # api-gateway: JwtAuthenticationFilter implements GlobalFilter
    resources/
      application.yml
      bootstrap.yml               # api-gateway: import từ config-server
```

---

## 4. ai-service

Stateless — **không** có `entity/`, `repository/`, `db/migration/`:

```
services/ai-service/
  pom.xml
  src/main/java/com/finance/ai/
    AiServiceApplication.java
    controller/                   # ChatController, ParseController
    dto/
    config/                       # AiConfig (ChatClient bean), AiProperties, SecurityConfig
    security/                     # JwtAuthenticationFilter
    feign/                        # @FeignClient + FeignAuthInterceptor
  src/main/resources/
    application.yml               # Spring AI Vertex Gemini cấu hình
    bootstrap.yml
```

---

## 5. Quy tắc đặt package

- Tất cả ở dưới `com.finance.<service>` (ví dụ `com.finance.auth`, `com.finance.transaction`).
- **Không** chia sẻ entity/dto giữa service qua module Maven chung — mỗi service tự định nghĩa DTO riêng (giảm coupling). Nếu thực sự cần dùng chung sau này (ví dụ event), tạo module `services/common-events`.

---

## 6. Quy tắc đặt tên Maven

- `groupId`: `com.finance`
- `artifactId`: bằng tên thư mục service (`auth-service`, `transaction-service`, …)
- `version`: kế thừa từ parent (`1.0.0-SNAPSHOT`)

---

## 7. Liên kết

- Stack chi tiết: [tech-stack.md](tech-stack.md)
- Layer code: [backend-conventions.md](backend-conventions.md)
- Database & Flyway: [database.md](database.md)

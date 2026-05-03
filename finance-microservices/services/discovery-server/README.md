# discovery-server

**Spring Cloud Netflix Eureka Server** chạy ở port `8761`. Tất cả business service và `api-gateway` đăng ký tại đây.

## Truy cập dashboard

```
http://localhost:8761/
```

## Chạy local

```bash
mvn -pl services/discovery-server -am spring-boot:run
```

## Cấu hình Eureka client cho service khác

```yaml
eureka:
  client:
    service-url:
      defaultZone: http://discovery-server:8761/eureka/
```

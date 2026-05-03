# Error handling — Spring Boot

## 1. Mô hình lỗi thống nhất — RFC 7807 ProblemDetail

Mỗi service business có `@RestControllerAdvice GlobalExceptionHandler` chuyển exception thành `ProblemDetail` (Spring 6).

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<ProblemDetail> handleApi(ApiException ex) {
        ProblemDetail body = ProblemDetail.forStatusAndDetail(ex.getStatus(), ex.getMessage());
        return ResponseEntity.status(ex.getStatus()).body(body);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail body = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Dữ liệu không hợp lệ");
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(fe -> errors.put(fe.getField(), fe.getDefaultMessage()));
        body.setProperty("errors", errors);
        return ResponseEntity.badRequest().body(body);
    }
}
```

## 2. ApiException

```java
@Getter
public class ApiException extends RuntimeException {
    private final HttpStatus status;
    public ApiException(HttpStatus status, String message) {
        super(message);
        this.status = status;
    }
}
```

Sử dụng:

```java
throw new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy giao dịch");
throw new ApiException(HttpStatus.CONFLICT, "Username đã tồn tại");
```

## 3. Mapping HTTP

| Tình huống | Status | Cách phát |
|-----------|--------|-----------|
| Validation `@Valid` fail | 400 | Tự động — `MethodArgumentNotValidException` |
| Body JSON parse lỗi | 400 | `HttpMessageNotReadableException` (default Spring) |
| Thiếu / sai JWT | 401 | Gateway filter / SecurityConfig |
| Resource không thuộc user | 404 | `ApiException(NOT_FOUND, ...)` (không tiết lộ tồn tại) |
| Trùng unique (username/email) | 409 | `ApiException(CONFLICT, ...)` |
| Feign call fail | 502 | Custom handler `FeignException` (TODO) |
| Spring AI provider chưa cấu hình | 503 | Trả message kiểu stub trong controller |

## 4. Feign error decoder (gợi ý nâng cao)

```java
@Bean
public ErrorDecoder feignErrorDecoder() {
    return (methodKey, response) -> {
        if (response.status() == 404) {
            return new ApiException(HttpStatus.NOT_FOUND, "Resource not found at " + methodKey);
        }
        return new ApiException(HttpStatus.BAD_GATEWAY, "Downstream " + methodKey + " trả " + response.status());
    };
}
```

## 5. Reactive (api-gateway)

Gateway dùng WebFlux; trả lỗi qua `ServerHttpResponse`:

```java
exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
exchange.getResponse().getHeaders().add(WWW_AUTHENTICATE, "Bearer error=\"Invalid token\"");
return exchange.getResponse().setComplete();
```

## 6. Không leak stack trace ra client

- Production: `server.error.include-stacktrace: never` (mặc định Spring Boot).
- Log đầy đủ ở backend; client chỉ thấy `detail` ngắn gọn + (optional) request id.

## 7. Validation thông điệp

- Dùng tiếng Việt hoặc tiếng Anh nhất quán trong service. Theo product team — repo này: **tiếng Việt cho user-facing message**.
- Đặt qua `messages.properties` nếu cần i18n.

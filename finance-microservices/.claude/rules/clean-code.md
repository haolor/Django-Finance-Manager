# Clean code (Java / Spring Boot)

## 1. Nguyên tắc

- **SOLID**: service phụ thuộc abstraction (`Repository`, `*Client` Feign), không phụ thuộc concrete.
- **YAGNI**: không thêm API/feature “cho tương lai”. Microservice mỗi service nhỏ, single-purpose.
- **DRY** với mức độ: tránh duplicate logic trong cùng service. **Cho phép** lặp giữa các service (zero-coupling > zero-duplication).

## 2. Java idiom

- Hàm ngắn, mỗi hàm ≤ ~30 dòng. Tách helper khi quá dài.
- Tên rõ: `findActiveBudgetsForUser` thay vì `getData`.
- `record` cho DTO, immutable.
- `Optional` cho return-có-thể-null. KHÔNG `Optional` cho field hoặc parameter.
- Stream: dùng cho transform list ngắn; vòng `for` cho logic phức tạp dễ debug hơn.

## 3. Lombok đúng mức

- `@Slf4j`, `@Getter`, `@Setter`, `@Builder`, `@RequiredArgsConstructor` — OK.
- `@Data` trên entity: tránh (tạo `equals/hashCode` dùng tất cả field, gặp lazy collection sẽ N+1 hoặc StackOverflow).
- `@AllArgsConstructor` chỉ trên DTO/entity, không trên service (dùng `@RequiredArgsConstructor` để inject final field).

## 4. Spring idiom

- Constructor injection. Không `@Autowired` field.
- Bean Spring là singleton — không lưu state mutable trong bean.
- `@Transactional` trên service method, không trên controller.
- `@Service`, `@Repository`, `@RestController` đúng stereotype.

## 5. Tránh duplicate giữa service

- Logic “build finance context cho LLM” chỉ tồn tại ở **transaction-service**. `ai-service` gọi qua Feign — không tự tổng hợp dữ liệu chéo DB.
- Validation rules nghiệp vụ (số tiền > 0, ngày ≤ hôm nay) đặt ở service sở hữu entity.

## 6. Comment

- Không comment kiểu kể lại code (`// increment counter`).
- Comment khi: lý do khác thường, trade-off, ràng buộc nghiệp vụ ngầm, link bug/issue.
- Dùng `// TODO(scope): ...` có tên scope để dễ grep.

## 7. Logging

- `@Slf4j`. Level đúng:
  - `DEBUG` — flow chi tiết dev.
  - `INFO` — milestone (login success, transaction created).
  - `WARN` — sự cố không chặn (Feign retry, fallback).
  - `ERROR` — exception cần xử lý.
- KHÔNG log token, password hash, body request đầy đủ ở production.

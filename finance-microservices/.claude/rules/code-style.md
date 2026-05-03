# Code style (Java)

## 1. Định dạng

- **Google Java Style** (modified): 4 spaces (theo Spring convention), không tab.
- Dòng tối đa **120** ký tự.
- Một class một file. Tên file = tên public class.

## 2. Import

- Thứ tự: java.* → jakarta.* → org.* → com.* → static imports.
- Không wildcard import (`import java.util.*`).

## 3. Đặt tên

| Loại | Quy ước | Ví dụ |
|------|---------|-------|
| Package | lowercase, không underscore | `com.finance.transaction.controller` |
| Class | PascalCase | `TransactionController` |
| Interface | PascalCase, không prefix `I` | `TransactionRepository` |
| Method / field | camelCase | `findByUserId` |
| Constant | UPPER_SNAKE | `BEARER_PREFIX` |
| Generics | một chữ in hoa | `T`, `R`, `E` |

## 4. Annotation

- Mỗi annotation trên một dòng cho class/method.
- Annotation field: cùng dòng nếu ngắn.

## 5. Spotless / Checkstyle (gợi ý — chưa cấu hình)

Khi muốn enforce, thêm vào parent `pom.xml`:

```xml
<plugin>
    <groupId>com.diffplug.spotless</groupId>
    <artifactId>spotless-maven-plugin</artifactId>
    <version>2.43.0</version>
    <configuration>
        <java>
            <googleJavaFormat>
                <version>1.22.0</version>
                <style>AOSP</style>
            </googleJavaFormat>
            <removeUnusedImports/>
        </java>
    </configuration>
</plugin>
```

## 6. SQL (Flyway)

- Từ khóa `UPPER CASE`, identifier snake_case.
- Mỗi statement kết thúc `;`.
- Comment Flyway ở đầu file: `-- V{n}: lý do`.

## 7. application.yml

- Indent **2 spaces**.
- Quote `"..."` cho giá trị có ký tự đặc biệt (`*`, `:`...).
- Đặt env override với mặc định: `${VAR:default}`.

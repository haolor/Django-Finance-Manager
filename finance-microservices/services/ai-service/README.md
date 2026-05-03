# ai-service

Microservice **AI/NLP** dùng **Spring AI + Google Gemini** (qua Vertex AI). Stateless, không có database.

- Port: `8085`.
- Provider mặc định: `gemini`. Model: `gemini-2.0-flash`.

## Endpoint

| Method | Path | Trạng thái | Mô tả |
|--------|------|-----------|-------|
| POST | `/v1/chat` | working | Chat có ngữ cảnh tài chính (gọi `transaction-service` qua Feign để lấy `finance-context`). |
| POST | `/v1/parse-transaction` | TODO (501) | Trích xuất `amount`, `category`, `date` từ câu tự nhiên rồi tạo giao dịch qua Feign. |
| GET | `/v1/predictions` | TODO | Dự đoán chi tiêu LLM, fallback Core. |

## Cấu hình LLM

Spring AI Vertex Gemini:

```yaml
spring:
  ai:
    vertex:
      ai:
        gemini:
          project-id: ${VERTEX_PROJECT_ID}
          location: us-central1
```

Yêu cầu **Application Default Credentials** (ADC) — đặt biến `GOOGLE_APPLICATION_CREDENTIALS` trỏ tới file service-account JSON, hoặc chạy trên hạ tầng GCP.

Khi chưa cấu hình, `ChatController` trả message `stub` — service vẫn boot được.

## Auth

- Tin tưởng `X-User-Id`/`X-Username` từ `api-gateway`.
- `FeignAuthInterceptor` forward `Authorization`, `X-User-Id`, `X-Username` xuống các service nội bộ.

## Biến môi trường

| Biến | Ý nghĩa |
|------|---------|
| `VERTEX_PROJECT_ID` | GCP project có Vertex AI |
| `VERTEX_LOCATION` | mặc định `us-central1` |
| `GEMINI_MODEL` | `gemini-2.0-flash` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path tới service-account JSON |
| `JWT_SECRET` | Cùng giá trị với gateway |

## Chạy local

```bash
mvn -pl services/ai-service -am spring-boot:run
```

# 🔔 Sửa Lỗi Thông Báo Giao Dịch Bất Thường

## Vấn đề
Icon "bell" (chuông thông báo) không hiển thị khi có giao dịch bất thường được tạo.

## Nguyên nhân
Trước đây, hệ thống chỉ tự động tạo thông báo cho:
- ✅ Giao dịch lớn (vượt ngưỡng tiền)
- ✅ Vượt ngân sách

Nhưng **KHÔNG** tự động phát hiện và tạo thông báo cho giao dịch bất thường (anomaly).

Chức năng phát hiện anomaly chỉ được gọi khi:
- User vào trang "AI Insights"
- User hỏi chatbot "Có giao dịch bất thường nào không?"

## Giải pháp
Đã thêm logic tự động phát hiện anomaly và tạo notification khi có transaction mới được tạo.

### Thay đổi trong `finance/views.py`:

#### 1. Phương thức `perform_create()` (TransactionViewSet)
Khi tạo transaction qua form:
```python
def perform_create(self, serializer):
    transaction = serializer.save(user=self.request.user)
    
    # Kiểm tra và tạo notifications
    check_large_transaction(transaction)
    if transaction.category:
        check_budget_exceeded(self.request.user, transaction.category)
    
    # ✨ THÊM MỚI: Kiểm tra anomaly tự động
    try:
        anomalies = AIService.detect_anomalies(self.request.user, days=30)
        for anomaly in anomalies:
            if anomaly['id'] == transaction.id:
                anomaly_data = {
                    'transaction': transaction,
                    'amount': transaction.amount,
                    'category': transaction.category.name if transaction.category else 'Khác',
                }
                create_anomaly_notification(self.request.user, anomaly_data)
                break
    except Exception as e:
        print(f"Error detecting anomaly: {e}")
```

#### 2. Phương thức `nlp_input()` (TransactionViewSet)
Khi tạo transaction qua NLP (nhập tự nhiên):
- Đã thêm logic tương tự để phát hiện anomaly tự động

## Cách hoạt động
1. User tạo giao dịch mới (qua form hoặc NLP)
2. Hệ thống kiểm tra:
   - ✅ Có phải giao dịch lớn không?
   - ✅ Có vượt ngân sách không?
   - ✅ **Có phải giao dịch bất thường không? (MỚI)**
3. Nếu phát hiện anomaly:
   - Tạo notification với type = 'anomaly_detected'
   - Notification hiển thị trong icon bell
   - User nhận được cảnh báo ngay lập tức

## Điều kiện phát hiện anomaly
Một giao dịch được coi là bất thường khi:
- Số tiền vượt quá **2 độ lệch chuẩn** (2σ) so với chi tiêu trung bình trong 30 ngày gần nhất
- Ví dụ: Nếu bạn thường chi 50k-100k cho ăn uống, nhưng đột nhiên chi 500k thì sẽ được đánh dấu là bất thường

## Cài đặt Notification
User có thể bật/tắt thông báo anomaly trong **Cài đặt > Thông báo**:
- "Phát hiện giao dịch bất thường" checkbox

## Kiểm tra
Để test:
1. Tạo một giao dịch với số tiền rất lớn so với thói quen chi tiêu
2. Kiểm tra icon bell (chuông) trên header
3. Số lượng thông báo chưa đọc sẽ tăng lên
4. Click vào bell để xem chi tiết notification

---
**Ngày sửa:** 17/01/2026
**File thay đổi:** `finance/views.py`

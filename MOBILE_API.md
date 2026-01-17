# Mobile API Documentation - Đồng bộ dữ liệu

Tài liệu này mô tả các API endpoints để đồng bộ dữ liệu giữa ứng dụng mobile và server.

## Base URL

### Development (Local Network):
```
http://YOUR_IP_ADDRESS:8000/api/
```

**Tìm IP address của máy tính:**
- Windows: `ipconfig` → Tìm "IPv4 Address"
- Mac/Linux: `ifconfig` hoặc `ip addr show`

Ví dụ: `http://192.168.100.137:8000/api/`

### Localhost (Chỉ từ máy tính):
```
http://localhost:8000/api/
```

## Authentication

Tất cả các endpoints (trừ đăng nhập/đăng ký) đều yêu cầu authentication token.

### Đăng nhập
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "demo_user",
  "password": "demo123"
}
```

**Response:**
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com"
  }
}
```

Lưu token này và gửi kèm trong header của mọi request:
```http
Authorization: Token abc123...
```

---

## 1. Đồng bộ tất cả dữ liệu (Khuyến nghị)

Endpoint này cho phép lấy tất cả dữ liệu (transactions, budgets, categories) trong một request duy nhất.

### GET /api/sync/all/

**Query Parameters:**
- `last_sync` (optional): ISO datetime string - Thời điểm sync cuối cùng. Ví dụ: `2024-01-15T10:30:00Z`
- `transactions_limit` (optional): Số lượng transactions tối đa (mặc định: 100)
- `budgets_limit` (optional): Số lượng budgets tối đa (mặc định: 50)

**Ví dụ:**
```http
GET /api/sync/all/?last_sync=2024-01-15T10:30:00Z&transactions_limit=200
Authorization: Token abc123...
```

**Response:**
```json
{
  "transactions": {
    "data": [
      {
        "id": 1,
        "category": 1,
        "category_name": "Ăn uống",
        "category_icon": "🍔",
        "category_color": "#3B82F6",
        "category_type": "expense",
        "amount": "50000.00",
        "description": "Bữa trưa",
        "transaction_date": "2024-01-15",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "count": 1,
    "has_more": false
  },
  "budgets": {
    "data": [...],
    "count": 0,
    "has_more": false
  },
  "categories": {
    "data": [...],
    "count": 10
  },
  "server_time": "2024-01-16T08:00:00Z",
  "last_sync": "2024-01-15T10:30:00Z"
}
```

**Lưu ý:**
- Nếu `has_more: true`, bạn cần gọi lại với `last_sync` mới để lấy thêm dữ liệu
- Lưu `server_time` để dùng làm `last_sync` cho lần sync tiếp theo

---

## 2. Đồng bộ Transactions riêng

### GET /api/transactions/sync/

**Query Parameters:**
- `last_sync` (optional): ISO datetime string
- `limit` (optional): Số lượng tối đa (mặc định: 100)

**Ví dụ:**
```http
GET /api/transactions/sync/?last_sync=2024-01-15T10:30:00Z&limit=50
Authorization: Token abc123...
```

**Response:**
```json
{
  "transactions": [...],
  "count": 10,
  "server_time": "2024-01-16T08:00:00Z",
  "has_more": false
}
```

---

## 3. Đồng bộ Bulk (Gửi dữ liệu từ mobile lên server)

### POST /api/transactions/bulk_sync/

Cho phép gửi nhiều transactions cùng lúc để tạo/cập nhật/xóa.

**Request Body:**
```json
{
  "transactions": [
    {
      "id": 1,
      "amount": "100000.00",
      "description": "Cập nhật mô tả",
      "transaction_date": "2024-01-15",
      "category": 1
    },
    {
      "amount": "50000.00",
      "description": "Giao dịch mới",
      "transaction_date": "2024-01-16",
      "category": 2
    }
  ],
  "deleted_ids": [3, 4]
}
```

**Lưu ý:**
- Nếu transaction có `id` → Cập nhật transaction đó
- Nếu transaction không có `id` → Tạo mới
- `deleted_ids`: Danh sách IDs của transactions đã xóa trên mobile

**Response:**
```json
{
  "success": true,
  "results": {
    "created": [
      {
        "id": 5,
        "amount": "50000.00",
        ...
      }
    ],
    "updated": [
      {
        "id": 1,
        "amount": "100000.00",
        ...
      }
    ],
    "deleted": [3, 4],
    "deleted_count": 2,
    "errors": []
  },
  "summary": {
    "created_count": 1,
    "updated_count": 1,
    "deleted_count": 2,
    "error_count": 0
  }
}
```

---

## 4. Đồng bộ Budgets

### GET /api/budgets/sync/

**Query Parameters:**
- `last_sync` (optional): ISO datetime string
- `limit` (optional): Số lượng tối đa (mặc định: 50)

**Ví dụ:**
```http
GET /api/budgets/sync/?last_sync=2024-01-15T10:30:00Z
Authorization: Token abc123...
```

---

## 5. Lấy danh sách Categories

Categories là dữ liệu shared (không phụ thuộc user), nên chỉ cần lấy một lần.

### GET /api/categories/

**Ví dụ:**
```http
GET /api/categories/
Authorization: Token abc123...
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ăn uống",
    "description": "Chi phí ăn uống",
    "icon": "🍔",
    "color": "#3B82F6",
    "type": "expense",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

## Chiến lược đồng bộ khuyến nghị

### Lần đầu tiên (Initial Sync)
1. Gọi `GET /api/sync/all/` (không có `last_sync`)
2. Lưu tất cả dữ liệu vào local database
3. Lưu `server_time` từ response

### Đồng bộ định kỳ (Periodic Sync)
1. Gọi `GET /api/sync/all/?last_sync={last_saved_server_time}`
2. Cập nhật/xóa dữ liệu local dựa trên response
3. Cập nhật `last_sync` = `server_time` mới

### Đồng bộ khi có thay đổi trên mobile (Push Sync)
1. Khi user tạo/sửa/xóa trên mobile:
   - Lưu vào local database với flag `pending_sync = true`
   - Gọi `POST /api/transactions/bulk_sync/` với dữ liệu pending
   - Nếu thành công, xóa flag `pending_sync`
   - Nếu thất bại, giữ lại để retry sau

### Xử lý conflict
- Nếu server trả về transaction với `updated_at` mới hơn local → Cập nhật local
- Nếu local có `updated_at` mới hơn server → Gửi lên server qua `bulk_sync`
- Nếu cả hai đều mới → Ưu tiên server (hoặc hỏi user)

---

## Error Handling

Tất cả các endpoints có thể trả về các lỗi sau:

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
→ Cần đăng nhập lại và lấy token mới

**400 Bad Request:**
```json
{
  "error": "Invalid data",
  "details": {...}
}
```

**500 Internal Server Error:**
→ Retry sau một khoảng thời gian

---

## Best Practices

1. **Lưu trữ local:**
   - Lưu `last_sync` timestamp sau mỗi lần sync thành công
   - Lưu token authentication an toàn (Keychain/Keystore)

2. **Offline Support:**
   - Cho phép user thao tác offline
   - Đánh dấu dữ liệu đã thay đổi cần sync
   - Sync khi có kết nối mạng

3. **Performance:**
   - Sync incremental (chỉ lấy dữ liệu mới) thay vì full sync
   - Sử dụng `limit` hợp lý để tránh quá tải
   - Cache categories (ít thay đổi)

4. **User Experience:**
   - Hiển thị indicator khi đang sync
   - Cho phép user cancel sync nếu cần
   - Thông báo khi sync thành công/thất bại

---

## Ví dụ code (Pseudo-code)

```javascript
// Initial Sync
async function initialSync() {
  const response = await fetch('/api/sync/all/', {
    headers: {
      'Authorization': `Token ${token}`
    }
  });
  const data = await response.json();
  
  // Save to local database
  await saveTransactions(data.transactions.data);
  await saveBudgets(data.budgets.data);
  await saveCategories(data.categories.data);
  
  // Save last sync time
  await saveLastSync(data.server_time);
}

// Periodic Sync
async function periodicSync() {
  const lastSync = await getLastSync();
  const url = lastSync 
    ? `/api/sync/all/?last_sync=${lastSync}`
    : '/api/sync/all/';
    
  const response = await fetch(url, {
    headers: {
      'Authorization': `Token ${token}`
    }
  });
  const data = await response.json();
  
  // Update local data
  await updateLocalData(data);
  await saveLastSync(data.server_time);
}

// Push pending changes
async function pushPendingChanges() {
  const pendingTransactions = await getPendingTransactions();
  
  const response = await fetch('/api/transactions/bulk_sync/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      transactions: pendingTransactions,
      deleted_ids: await getDeletedIds()
    })
  });
  
  const result = await response.json();
  if (result.success) {
    await clearPendingFlags();
  }
}
```

---

## Testing

Bạn có thể test các endpoints bằng:
- Postman
- curl
- Mobile app development tools

**Ví dụ với curl:**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo123"}'

# Sync all
curl -X GET "http://localhost:8000/api/sync/all/" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```


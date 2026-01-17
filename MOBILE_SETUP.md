# Hướng dẫn Setup Mobile App

Hướng dẫn chi tiết để kết nối mobile app với Django API server.

## Bước 1: Tìm IP Address của máy tính

### Windows:
```powershell
ipconfig
```
Tìm dòng **IPv4 Address**, ví dụ: `192.168.100.137`

### Mac/Linux:
```bash
ifconfig | grep "inet "
```
Hoặc:
```bash
ip addr show
```

### Lưu ý:
- IP này phải cùng mạng WiFi với điện thoại của bạn
- IP có thể thay đổi mỗi lần kết nối WiFi mới

---

## Bước 2: Cấu hình Django Server

### 2.1. Cập nhật settings.py

File `mysite/settings.py` đã được cấu hình để cho phép truy cập từ mạng local.

### 2.2. Chạy server với IP address

**Thay vì chạy:**
```bash
py manage.py runserver
```

**Chạy với IP address:**
```bash
py manage.py runserver 0.0.0.0:8000
```

Hoặc với IP cụ thể:
```bash
py manage.py runserver 192.168.100.137:8000
```

**Lưu ý:** `0.0.0.0` cho phép truy cập từ mọi IP trong mạng local.

---

## Bước 3: Kiểm tra kết nối

### 3.1. Từ máy tính:
Mở browser và truy cập:
```
http://192.168.100.137:8000/api/
```

### 3.2. Từ điện thoại (cùng WiFi):
Mở browser trên điện thoại và truy cập:
```
http://192.168.100.137:8000/api/
```

Nếu thấy JSON response → Kết nối thành công! ✅

---

## Bước 4: Cấu hình Mobile App

### Base URL trong Mobile App

Thay vì `http://localhost:8000`, sử dụng IP address:

```javascript
// React Native / JavaScript
const API_BASE_URL = 'http://192.168.100.137:8000/api';
```

```dart
// Flutter
const String API_BASE_URL = 'http://192.168.100.137:8000/api';
```

```kotlin
// Android (Kotlin)
const val API_BASE_URL = "http://192.168.100.137:8000/api"
```

```swift
// iOS (Swift)
let API_BASE_URL = "http://192.168.100.137:8000/api"
```

---

## Bước 5: Xử lý lỗi thường gặp

### Lỗi: "Connection refused" hoặc "Network error"

**Nguyên nhân:**
- IP address không đúng
- Server chưa chạy với `0.0.0.0:8000`
- Điện thoại và máy tính không cùng WiFi
- Firewall chặn kết nối

**Giải pháp:**
1. Kiểm tra IP address lại: `ipconfig` (Windows) hoặc `ifconfig` (Mac/Linux)
2. Đảm bảo chạy server với: `py manage.py runserver 0.0.0.0:8000`
3. Kiểm tra cả hai thiết bị đều cùng WiFi
4. Tắt Windows Firewall tạm thời hoặc thêm exception cho port 8000

### Lỗi: "CORS policy" hoặc "Access-Control-Allow-Origin"

**Nguyên nhân:**
- CORS chưa được cấu hình đúng

**Giải pháp:**
- File `mysite/settings.py` đã được cấu hình `CORS_ALLOW_ALL_ORIGINS = True` trong DEBUG mode
- Nếu vẫn lỗi, kiểm tra lại cài đặt `corsheaders` trong `INSTALLED_APPS` và `MIDDLEWARE`

### Lỗi: "DisallowedHost"

**Nguyên nhân:**
- IP address chưa được thêm vào `ALLOWED_HOSTS`

**Giải pháp:**
- Đã cấu hình `ALLOWED_HOSTS = ['*']` trong development mode
- Nếu vẫn lỗi, thêm IP cụ thể vào `ALLOWED_HOSTS`

---

## Bước 6: Sử dụng Ngrok (Tùy chọn - Cho truy cập từ xa)

Nếu muốn truy cập từ bất kỳ đâu (không cần cùng WiFi), sử dụng Ngrok:

### 6.1. Cài đặt Ngrok:
```bash
# Download từ https://ngrok.com/download
# Hoặc với npm:
npm install -g ngrok
```

### 6.2. Chạy Ngrok:
```bash
ngrok http 8000
```

### 6.3. Lấy URL:
Ngrok sẽ cung cấp URL dạng:
```
https://abc123.ngrok.io
```

### 6.4. Sử dụng trong Mobile App:
```javascript
const API_BASE_URL = 'https://abc123.ngrok.io/api';
```

**Lưu ý:**
- URL Ngrok thay đổi mỗi lần chạy (trừ khi dùng tài khoản trả phí)
- Chỉ dùng cho development, không dùng cho production

---

## Ví dụ Code Mobile App

### React Native với Axios

```javascript
import axios from 'axios';

// Cấu hình API
const API_BASE_URL = 'http://192.168.100.137:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Thêm token vào header
api.interceptors.request.use((config) => {
  const token = AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Đăng nhập
export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/login/', {
      username,
      password,
    });
    await AsyncStorage.setItem('token', response.data.token);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Đồng bộ dữ liệu
export const syncAll = async (lastSync = null) => {
  try {
    const params = lastSync ? { last_sync: lastSync } : {};
    const response = await api.get('/sync/all/', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Bulk sync
export const bulkSync = async (transactions, deletedIds = []) => {
  try {
    const response = await api.post('/transactions/bulk_sync/', {
      transactions,
      deleted_ids: deletedIds,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};
```

### Flutter với http package

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String BASE_URL = 'http://192.168.100.137:8000/api';
  
  // Lấy token
  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }
  
  // Lưu token
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }
  
  // Tạo headers với token
  Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }
  
  // Đăng nhập
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$BASE_URL/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveToken(data['token']);
      return data;
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }
  
  // Đồng bộ tất cả
  Future<Map<String, dynamic>> syncAll({String? lastSync}) async {
    final headers = await _getHeaders();
    final uri = lastSync != null
        ? Uri.parse('$BASE_URL/sync/all/?last_sync=$lastSync')
        : Uri.parse('$BASE_URL/sync/all/');
    
    final response = await http.get(uri, headers: headers);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Sync failed: ${response.body}');
    }
  }
  
  // Bulk sync
  Future<Map<String, dynamic>> bulkSync(
    List<Map<String, dynamic>> transactions,
    List<int> deletedIds,
  ) async {
    final headers = await _getHeaders();
    final response = await http.post(
      Uri.parse('$BASE_URL/transactions/bulk_sync/'),
      headers: headers,
      body: jsonEncode({
        'transactions': transactions,
        'deleted_ids': deletedIds,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Bulk sync failed: ${response.body}');
    }
  }
}
```

---

## Checklist Setup

- [ ] Tìm IP address của máy tính
- [ ] Cập nhật `ALLOWED_HOSTS` trong `settings.py` (đã làm)
- [ ] Cập nhật `CORS_ALLOWED_ORIGINS` (đã làm)
- [ ] Chạy server với `0.0.0.0:8000`
- [ ] Kiểm tra kết nối từ browser trên điện thoại
- [ ] Cấu hình Base URL trong mobile app
- [ ] Test đăng nhập từ mobile app
- [ ] Test sync dữ liệu từ mobile app

---

## Production Deployment

Khi deploy lên production:

1. **Thay đổi `DEBUG = False`** trong `settings.py`
2. **Cấu hình `ALLOWED_HOSTS`** với domain thực tế:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```
3. **Cấu hình `CORS_ALLOWED_ORIGINS`** với domain mobile app:
   ```python
   CORS_ALLOWED_ORIGINS = [
       'https://yourdomain.com',
       'https://api.yourdomain.com',
   ]
   ```
4. **Sử dụng HTTPS** (bắt buộc cho production)
5. **Cấu hình reverse proxy** (Nginx/Apache)
6. **Sử dụng database production** (PostgreSQL trên server)

---

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Server logs: `py manage.py runserver 0.0.0.0:8000`
2. Network connectivity: Ping từ điện thoại đến IP máy tính
3. Firewall settings: Đảm bảo port 8000 không bị chặn
4. API documentation: Xem file `MOBILE_API.md`


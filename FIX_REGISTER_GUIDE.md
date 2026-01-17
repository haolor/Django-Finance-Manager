# 🔧 Hướng Dẫn Sửa Lỗi Đăng Ký

## ✅ Kết Quả Kiểm Tra

**Backend:** ✅ Hoạt động HOÀN HẢO (tất cả test đều PASSED)

**Vấn đề có thể:**
1. Frontend chưa build
2. Server chưa chạy
3. Port không đúng

---

## 🚀 Giải Pháp Nhanh (Làm Theo Thứ Tự)

### Cách 1: Dùng File Test HTML (ĐƠN GIẢN NHẤT)

1. **Mở file test:** 
   - Mở file `test_register.html` bằng browser
   - Hoặc: http://localhost:8000/test_register.html (nếu đã copy vào static)

2. **Điền thông tin:**
   - Username: `testuser999`
   - Password: `testpass123`
   - Confirm: `testpass123`

3. **Nhấn "Đăng Ký"**
   - ✅ Nếu thấy "Kết nối API thành công" → Backend OK
   - ❌ Nếu lỗi "Không thể kết nối" → Server chưa chạy

**File test_register.html sẽ:**
- ✅ Hiển thị lỗi chi tiết
- ✅ Show debug information
- ✅ Test kết nối API trực tiếp

---

### Cách 2: Chạy Frontend + Backend Đúng Cách

#### Terminal 1: Chạy Backend
```bash
cd C:\Users\Admin\Django-Finance-Manager
py manage.py runserver 0.0.0.0:8000
```

Chờ thấy message:
```
Starting development server at http://0.0.0.0:8000/
```

#### Terminal 2: Chạy Frontend (Development)
```bash
cd C:\Users\Admin\Django-Finance-Manager\frontend
npm run dev
```

Hoặc nếu muốn dùng build version:
```bash
npm run build
```

Sau đó mở:
- **Development:** http://localhost:3000/register
- **Production:** http://localhost:8000/register

---

## 🐛 Debug Chi Tiết

### Bước 1: Kiểm Tra Server

```bash
# Terminal 1
cd C:\Users\Admin\Django-Finance-Manager
py manage.py runserver 0.0.0.0:8000
```

Phải thấy:
```
✅ System check identified no issues
✅ Starting development server at http://0.0.0.0:8000/
```

### Bước 2: Test API Trực Tiếp

Mở browser và vào: http://localhost:8000/api/

Phải thấy JSON response:
```json
{
  "message": "Finance Management System API",
  "version": "1.0.0",
  ...
}
```

### Bước 3: Test Endpoint Đăng Ký

**Option A: Dùng test_register.html**
- Mở file `test_register.html` trong browser
- Thử đăng ký
- Xem debug info

**Option B: Dùng Browser Console**
```javascript
// Mở Console (F12) và paste:
fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser999',
    password: 'testpass123',
    password_confirm: 'testpass123'
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

Nếu thành công, sẽ thấy:
```json
{
  "token": "abc123...",
  "user": { "username": "testuser999", ... }
}
```

### Bước 4: Kiểm Tra Frontend

1. **Mở Developer Tools (F12)**
2. **Vào tab Console** - xem có lỗi JavaScript không
3. **Vào tab Network** - xem request/response

Khi đăng ký, phải thấy:
- Request: `POST /api/auth/register/`
- Status: `201 Created` (thành công) hoặc `400 Bad Request` (lỗi validation)

---

## 🔍 Các Lỗi Thường Gặp

### ❌ Lỗi: "Failed to fetch" / "Network Error"

**Nguyên nhân:** Server Django không chạy

**Giải pháp:**
```bash
py manage.py runserver 0.0.0.0:8000
```

---

### ❌ Lỗi: "CORS policy"

**Nguyên nhân:** Frontend chạy trên domain khác

**Đã sửa trong settings.py:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # OK cho development
```

Nếu vẫn lỗi, restart server Django.

---

### ❌ Lỗi: 400 Bad Request - "Passwords do not match"

**Nguyên nhân:** Mật khẩu và xác nhận không giống nhau

**Giải pháp:** Gõ lại mật khẩu chính xác

---

### ❌ Lỗi: 400 Bad Request - "Username already exists"

**Nguyên nhân:** Username đã có người dùng

**Giải pháp:** 

**Option 1:** Chọn username khác

**Option 2:** Xóa user cũ
```bash
py manage.py shell
```
```python
from django.contrib.auth.models import User
User.objects.filter(username='testuser999').delete()
exit()
```

---

### ❌ Lỗi: "This field is required"

**Nguyên nhân:** Thiếu username hoặc password

**Giải pháp:** Điền đầy đủ thông tin bắt buộc:
- Username ✅
- Password ✅  
- Password Confirm ✅

---

## 📋 Checklist Hoàn Chỉnh

- [ ] Server Django đang chạy: `py manage.py runserver 0.0.0.0:8000`
- [ ] Test API: http://localhost:8000/api/ (phải thấy JSON)
- [ ] Test endpoint: Dùng `test_register.html`
- [ ] Mở F12 để xem Console và Network tab
- [ ] Username chưa tồn tại
- [ ] Mật khẩu ≥ 8 ký tự
- [ ] Password và Confirm giống nhau

---

## 🎯 Test Scripts Có Sẵn

### 1. test_register.py
```bash
py test_register.py
```
Test backend API (không cần browser)

### 2. test_register.html
Mở file này trong browser để test với UI đẹp

### 3. test_email.py
```bash
py test_email.py
```
Test email notification (nếu cần)

---

## 💡 Tips

### Xem Log Chi Tiết

**Server Django:**
- Mở terminal chạy Django
- Mỗi request sẽ hiện log
- Nếu có lỗi 500, sẽ thấy traceback

**Browser Console:**
```javascript
// Enable verbose logging
localStorage.debug = '*'
```

### Reset Frontend

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Reset Database (nếu cần)

```bash
py manage.py migrate
py manage.py createsuperuser
```

---

## 📞 Nếu Vẫn Không Được

Gửi cho tôi screenshot của:

1. **Terminal chạy Django** - để xem server có chạy không
2. **Browser Console (F12)** - để xem lỗi JavaScript
3. **Network Tab** - request `/api/auth/register/` và response
4. **Form đăng ký** - với thông tin bạn đã nhập

---

## ✅ Tóm Tắt

| Bước | Lệnh | Kết Quả Mong Đợi |
|------|------|------------------|
| 1 | `py test_register.py` | ✅ Tất cả test PASSED |
| 2 | `py manage.py runserver 0.0.0.0:8000` | ✅ Server starting... |
| 3 | Mở http://localhost:8000/api/ | ✅ Thấy JSON API |
| 4 | Mở `test_register.html` | ✅ Test đăng ký thành công |
| 5 | Vào trang web thật và đăng ký | ✅ Redirect sang Dashboard |

---

**Kết luận:** Backend hoạt động 100%. Nếu không đăng ký được trên web, vấn đề là:
- Server chưa chạy
- Frontend chưa kết nối đúng backend
- Browser cache (thử Ctrl+F5)

Hãy dùng `test_register.html` để test trước! 🚀

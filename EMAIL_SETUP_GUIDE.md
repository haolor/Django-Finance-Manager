# 📧 Hướng Dẫn Kiểm Tra và Cấu Hình Email Notification

## 🔍 Tình Trạng Hiện Tại

**Chức năng gửi email CHƯA được implement!** 

Trong file `finance/notification_service.py`, chỉ có comment TODO:
```python
# TODO: Gửi email nếu send_email=True
# if send_email:
#     send_notification_email(notification)
```

Hiện tại các notification chỉ hiển thị trong ứng dụng (icon bell), KHÔNG gửi qua email.

---

## 🛠️ Cách Implement Chức Năng Gửi Email

### Bước 1: Cấu hình Email trong Django

Thêm vào file `mysite/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Option 1: Sử dụng Gmail
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Email của bạn
EMAIL_HOST_PASSWORD = 'your-app-password'  # App Password (không phải mật khẩu Gmail thông thường)
DEFAULT_FROM_EMAIL = 'Finance Manager <your-email@gmail.com>'

# Option 2: Sử dụng Outlook/Hotmail
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@outlook.com'
# EMAIL_HOST_PASSWORD = 'your-password'

# Option 3: Sử dụng SendGrid (recommended for production)
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

### Bước 2: Tạo App Password cho Gmail

**Quan trọng:** Không được dùng mật khẩu Gmail thông thường!

1. Vào [Google Account Security](https://myaccount.google.com/security)
2. Bật "2-Step Verification" (bắt buộc)
3. Vào "App passwords" (Mật khẩu ứng dụng)
4. Chọn "Mail" và "Other" (Custom name): "Django Finance"
5. Copy mật khẩu 16 ký tự được tạo
6. Dùng mật khẩu này trong `EMAIL_HOST_PASSWORD`

### Bước 3: Implement Hàm Gửi Email

Thêm vào file `finance/notification_service.py`:

```python
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_notification_email(notification):
    """Gửi email notification cho user"""
    try:
        user = notification.user
        if not user.email:
            print(f"User {user.username} không có email")
            return False
        
        # Tạo subject
        subject = f'[Finance Manager] {notification.title}'
        
        # Tạo HTML content
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #2563eb;">{notification.title}</h2>
                <p>{notification.message}</p>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #f3f4f6; border-left: 4px solid #2563eb;">
                    <p style="margin: 0;"><strong>Loại thông báo:</strong> {notification.get_type_display()}</p>
                    <p style="margin: 5px 0 0 0;"><strong>Thời gian:</strong> {notification.created_at.strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <hr style="margin: 20px 0;">
                
                <p style="color: #666; font-size: 12px;">
                    Bạn nhận được email này vì đã bật thông báo trong Finance Manager.<br>
                    Để thay đổi cài đặt, vui lòng truy cập <a href="http://localhost:8000/settings">Cài đặt</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
{notification.title}

{notification.message}

Loại thông báo: {notification.get_type_display()}
Thời gian: {notification.created_at.strftime('%d/%m/%Y %H:%M')}

---
Bạn nhận được email này vì đã bật thông báo trong Finance Manager.
        """
        
        # Gửi email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Cập nhật notification
        notification.email_sent = True
        notification.save()
        
        print(f"✅ Email sent to {user.email}: {notification.title}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
```

### Bước 4: Sửa Hàm create_notification

Trong file `finance/notification_service.py`, sửa:

```python
def create_notification(user, notification_type, title, message, related_transaction=None, related_budget=None, send_email=False):
    """Tạo một notification mới"""
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        related_transaction=related_transaction,
        related_budget=related_budget,
        email_sent=False
    )
    
    # Gửi email nếu send_email=True
    if send_email:
        send_notification_email(notification)
    
    return notification
```

---

## 🧪 Cách Kiểm Tra Email

### Test 1: Console Backend (Development)

Để test mà không cần cấu hình SMTP thật:

```python
# mysite/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Email sẽ được in ra console thay vì gửi thật.

### Test 2: File Backend

```python
# mysite/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

Email sẽ được lưu vào file trong thư mục `sent_emails/`.

### Test 3: Django Shell

```python
python manage.py shell
```

Trong shell:
```python
from django.core.mail import send_mail
from django.conf import settings

# Test gửi email đơn giản
send_mail(
    subject='Test Email',
    message='Đây là email test từ Finance Manager',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-test-email@gmail.com'],
    fail_silently=False,
)
```

Nếu thành công, bạn sẽ thấy message: `1` (nghĩa là 1 email đã được gửi)

### Test 4: Test Notification Real

```python
python manage.py shell
```

```python
from django.contrib.auth.models import User
from finance.models import UserPreferences
from finance.notification_service import create_notification

# Lấy user
user = User.objects.first()

# Đảm bảo user có email
if not user.email:
    user.email = 'your-test-email@gmail.com'
    user.save()

# Tạo notification với send_email=True
notification = create_notification(
    user=user,
    notification_type='large_transaction',
    title='Test Email Notification',
    message='Đây là test để kiểm tra gửi email có hoạt động không',
    send_email=True
)

print(f"Email sent: {notification.email_sent}")
```

### Test 5: Test Thực Tế Qua UI

1. **Đảm bảo user có email:**
   - Vào Django Admin: http://localhost:8000/admin
   - Chọn Users
   - Thêm email cho user của bạn

2. **Bật cấu hình gửi email:**
   - Vào Cài đặt > Thông báo
   - Tick vào các checkbox:
     - ☑️ "Giao dịch lớn"
     - ☑️ "Vượt ngân sách"
     - ☑️ "Phát hiện giao dịch bất thường"

3. **Tạo giao dịch test:**
   - Tạo một giao dịch với số tiền lớn (vượt ngưỡng)
   - Kiểm tra:
     - ✅ Notification xuất hiện trong icon bell
     - ✅ Email được gửi đến hộp thư

---

## 🔧 Troubleshooting

### Lỗi: "SMTPAuthenticationError"

**Nguyên nhân:** Sai email/password hoặc chưa bật App Password

**Giải pháp:**
- Đảm bảo dùng App Password, không phải mật khẩu Gmail thường
- Bật 2-Step Verification
- Kiểm tra email và password trong settings.py

### Lỗi: "Connection refused"

**Nguyên nhân:** Sai cấu hình SMTP host/port

**Giải pháp:**
- Gmail: `smtp.gmail.com:587` với TLS
- Outlook: `smtp-mail.outlook.com:587` với TLS

### Lỗi: "Email is empty"

**Nguyên nhân:** User không có email trong database

**Giải pháp:**
```python
from django.contrib.auth.models import User
user = User.objects.get(username='your-username')
user.email = 'your-email@gmail.com'
user.save()
```

### Email không được gửi nhưng không có lỗi

**Kiểm tra:**
1. User có email không?
2. Preferences có bật "notify_*" không?
3. `send_email=True` được truyền vào hàm create_notification không?

---

## 📊 Kiểm Tra Logs

Thêm logging để debug:

```python
# mysite/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'email_debug.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 🎯 Checklist Hoàn Chỉnh

- [ ] Cấu hình EMAIL_* trong settings.py
- [ ] Tạo App Password (nếu dùng Gmail)
- [ ] Implement hàm send_notification_email()
- [ ] Uncomment code gửi email trong create_notification()
- [ ] Test với console backend
- [ ] Test với SMTP thật
- [ ] Kiểm tra user có email trong database
- [ ] Bật notifications trong Settings UI
- [ ] Tạo transaction test và kiểm tra email

---

**Lưu ý Bảo Mật:**
- ❌ KHÔNG commit email/password vào Git
- ✅ Dùng environment variables:
  ```python
  import os
  EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
  ```
- ✅ Tạo file `.env` và thêm vào `.gitignore`

---

**Ngày tạo:** 17/01/2026
**Tình trạng:** Email notification chưa được implement (TODO)

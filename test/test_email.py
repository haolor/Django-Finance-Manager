"""
Script để test email notification
Chạy: python test_email.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from finance.notification_service import create_notification

def test_basic_email():
    """Test 1: Gửi email cơ bản"""
    print("\n" + "="*60)
    print("TEST 1: Gửi email cơ bản")
    print("="*60)
    
    try:
        result = send_mail(
            subject='[TEST] Email từ Finance Manager',
            message='Đây là email test.\n\nNếu bạn nhận được email này, chức năng gửi email đã hoạt động!',
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@financemanager.com',
            recipient_list=[input("Nhập email của bạn để test: ").strip()],
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Email đã được gửi thành công!")
            print("📧 Kiểm tra hộp thư của bạn (bao gồm cả thư mục Spam)")
            return True
        else:
            print("❌ Email không được gửi")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")
        print("\nCó thể do:")
        print("- Chưa cấu hình EMAIL_HOST, EMAIL_PORT trong settings.py")
        print("- Sai EMAIL_HOST_USER hoặc EMAIL_HOST_PASSWORD")
        print("- Chưa bật App Password (nếu dùng Gmail)")
        return False

def test_notification_email():
    """Test 2: Gửi notification email thông qua hệ thống"""
    print("\n" + "="*60)
    print("TEST 2: Gửi notification qua hệ thống")
    print("="*60)
    
    # Kiểm tra xem có hàm send_notification_email không
    try:
        from finance.notification_service import send_notification_email
        has_function = True
    except ImportError:
        has_function = False
        print("⚠️  Chưa implement hàm send_notification_email()")
        print("📋 Xem hướng dẫn trong file EMAIL_SETUP_GUIDE.md")
        return False
    
    # Lấy user đầu tiên
    try:
        user = User.objects.first()
        if not user:
            print("❌ Không tìm thấy user nào trong database")
            print("Tạo user bằng: python manage.py createsuperuser")
            return False
        
        # Kiểm tra user có email không
        if not user.email:
            email = input(f"User '{user.username}' chưa có email. Nhập email: ").strip()
            user.email = email
            user.save()
            print(f"✅ Đã cập nhật email cho user {user.username}")
        
        print(f"📧 Sẽ gửi đến: {user.email}")
        
        # Tạo notification với send_email=True
        notification = create_notification(
            user=user,
            notification_type='large_transaction',
            title='🧪 Test Email Notification',
            message='Đây là email test từ Finance Manager.\n\nNếu bạn nhận được email này, hệ thống notification đã hoạt động đầy đủ!',
            send_email=True
        )
        
        if notification.email_sent:
            print("✅ Email notification đã được gửi!")
            print(f"📧 Kiểm tra email: {user.email}")
            return True
        else:
            print("⚠️  Notification được tạo nhưng email chưa được gửi")
            print("Có thể do send_email=True nhưng chưa implement send_notification_email()")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def check_settings():
    """Kiểm tra cấu hình email"""
    print("\n" + "="*60)
    print("KIỂM TRA CÁC CẤU HÌNH EMAIL")
    print("="*60)
    
    settings_to_check = [
        ('EMAIL_BACKEND', 'Backend email'),
        ('EMAIL_HOST', 'SMTP Host'),
        ('EMAIL_PORT', 'SMTP Port'),
        ('EMAIL_USE_TLS', 'Sử dụng TLS'),
        ('EMAIL_HOST_USER', 'Email gửi'),
        ('EMAIL_HOST_PASSWORD', 'Password (ẩn)'),
        ('DEFAULT_FROM_EMAIL', 'Email hiển thị'),
    ]
    
    print("\nCấu hình hiện tại:")
    for setting_name, description in settings_to_check:
        if hasattr(settings, setting_name):
            value = getattr(settings, setting_name)
            # Ẩn password
            if 'PASSWORD' in setting_name:
                value = '***' if value else '(Chưa cấu hình)'
            print(f"  ✅ {description:<25} : {value}")
        else:
            print(f"  ❌ {description:<25} : (Chưa cấu hình)")
    
    # Kiểm tra xem đã cấu hình đầy đủ chưa
    required = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
    missing = [s for s in required if not hasattr(settings, s) or not getattr(settings, s)]
    
    if missing:
        print(f"\n⚠️  Thiếu cấu hình: {', '.join(missing)}")
        print("📋 Xem hướng dẫn trong file EMAIL_SETUP_GUIDE.md")
        return False
    else:
        print("\n✅ Các cấu hình cần thiết đã đầy đủ")
        return True

def main():
    print("\n" + "="*60)
    print("🧪 TEST EMAIL NOTIFICATION - FINANCE MANAGER")
    print("="*60)
    
    # 1. Kiểm tra settings
    if not check_settings():
        print("\n❌ Vui lòng cấu hình email trong settings.py trước")
        print("📋 Xem hướng dẫn: EMAIL_SETUP_GUIDE.md")
        return
    
    # 2. Test email cơ bản
    choice = input("\nBạn có muốn test gửi email cơ bản? (y/n): ").strip().lower()
    if choice == 'y':
        test_basic_email()
    
    # 3. Test notification email
    choice = input("\nBạn có muốn test notification email? (y/n): ").strip().lower()
    if choice == 'y':
        test_notification_email()
    
    print("\n" + "="*60)
    print("TEST HOÀN TẤT")
    print("="*60)
    print("\n💡 Lưu ý:")
    print("- Kiểm tra cả thư mục Spam/Junk")
    print("- Nếu dùng Gmail, cần tạo App Password")
    print("- Đọc EMAIL_SETUP_GUIDE.md để biết chi tiết")
    print()

if __name__ == '__main__':
    main()

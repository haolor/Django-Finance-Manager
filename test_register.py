"""
Script để test chức năng đăng ký
Chạy: python test_register.py
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

def test_register():
    """Test chức năng đăng ký"""
    print("\n" + "="*60)
    print("🧪 TEST CHỨC NĂNG ĐĂNG KÝ")
    print("="*60)
    
    client = APIClient()
    
    # Test case 1: Đăng ký thành công
    print("\n📋 Test 1: Đăng ký với thông tin hợp lệ")
    print("-" * 60)
    
    # Xóa user test nếu đã tồn tại
    User.objects.filter(username='testuser123').delete()
    
    register_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    print(f"Request data: {json.dumps(register_data, indent=2, ensure_ascii=False)}")
    
    response = client.post('/api/auth/register/', register_data, format='json')
    
    print(f"\nStatus code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        print("✅ Test 1 PASSED: Đăng ký thành công!")
        print(f"   Token: {response.data.get('token', 'N/A')[:20]}...")
        print(f"   Username: {response.data.get('user', {}).get('username', 'N/A')}")
    else:
        print("❌ Test 1 FAILED: Đăng ký thất bại!")
        if response.status_code == 400:
            print("   Lỗi validation:")
            for field, errors in response.data.items():
                print(f"   - {field}: {errors}")
    
    # Test case 2: Mật khẩu không khớp
    print("\n📋 Test 2: Mật khẩu không khớp")
    print("-" * 60)
    
    User.objects.filter(username='testuser456').delete()
    
    register_data = {
        'username': 'testuser456',
        'email': 'test2@example.com',
        'password': 'testpass123',
        'password_confirm': 'differentpass',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = client.post('/api/auth/register/', register_data, format='json')
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 400:
        print("✅ Test 2 PASSED: Hệ thống đã từ chối mật khẩu không khớp")
    else:
        print("❌ Test 2 FAILED: Hệ thống không validate mật khẩu đúng")
    
    # Test case 3: Username đã tồn tại
    print("\n📋 Test 3: Username đã tồn tại")
    print("-" * 60)
    
    # Tạo user trước
    User.objects.filter(username='existinguser').delete()
    User.objects.create_user(username='existinguser', password='pass123')
    
    register_data = {
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
    }
    
    response = client.post('/api/auth/register/', register_data, format='json')
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 400:
        print("✅ Test 3 PASSED: Hệ thống đã từ chối username trùng")
    else:
        print("❌ Test 3 FAILED: Hệ thống cho phép username trùng")
    
    # Test case 4: Mật khẩu quá ngắn
    print("\n📋 Test 4: Mật khẩu quá ngắn (< 8 ký tự)")
    print("-" * 60)
    
    User.objects.filter(username='testuser789').delete()
    
    register_data = {
        'username': 'testuser789',
        'email': 'test3@example.com',
        'password': 'short',
        'password_confirm': 'short',
    }
    
    response = client.post('/api/auth/register/', register_data, format='json')
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 400:
        print("✅ Test 4 PASSED: Hệ thống đã từ chối mật khẩu quá ngắn")
    else:
        print("❌ Test 4 FAILED: Hệ thống cho phép mật khẩu quá ngắn")
    
    # Test case 5: Thiếu trường bắt buộc
    print("\n📋 Test 5: Thiếu trường bắt buộc (username)")
    print("-" * 60)
    
    register_data = {
        'email': 'test4@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
    }
    
    response = client.post('/api/auth/register/', register_data, format='json')
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 400:
        print("✅ Test 5 PASSED: Hệ thống đã từ chối request thiếu username")
    else:
        print("❌ Test 5 FAILED: Hệ thống không validate trường bắt buộc")
    
    # Cleanup
    print("\n🧹 Dọn dẹp data test...")
    User.objects.filter(username__in=['testuser123', 'testuser456', 'existinguser', 'testuser789']).delete()
    print("✅ Đã xóa các user test")

def check_endpoint():
    """Kiểm tra endpoint có tồn tại không"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA ENDPOINT")
    print("="*60)
    
    from django.urls import get_resolver
    from django.urls.resolvers import URLPattern, URLResolver
    
    def get_all_urls(resolver, prefix=''):
        urls = []
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLResolver):
                urls.extend(get_all_urls(pattern, prefix + str(pattern.pattern)))
            elif isinstance(pattern, URLPattern):
                url = prefix + str(pattern.pattern)
                urls.append(url)
        return urls
    
    resolver = get_resolver()
    all_urls = get_all_urls(resolver)
    
    # Tìm các endpoint auth
    auth_urls = [url for url in all_urls if 'auth' in url or 'register' in url]
    
    print("\n📍 Các endpoint liên quan đến auth:")
    for url in auth_urls:
        print(f"   {url}")
    
    if any('register' in url for url in auth_urls):
        print("\n✅ Endpoint /api/auth/register/ tồn tại")
    else:
        print("\n❌ Endpoint /api/auth/register/ KHÔNG tồn tại")
        print("Cần kiểm tra file urls.py")

def check_database():
    """Kiểm tra kết nối database"""
    print("\n" + "="*60)
    print("🗄️  KIỂM TRA DATABASE")
    print("="*60)
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Kết nối database thành công")
        
        # Kiểm tra bảng User
        user_count = User.objects.count()
        print(f"✅ Bảng User có {user_count} user")
        
    except Exception as e:
        print(f"❌ Lỗi database: {e}")

def main():
    print("\n" + "="*60)
    print("🧪 TEST HỆ THỐNG ĐĂNG KÝ - FINANCE MANAGER")
    print("="*60)
    
    # 1. Kiểm tra database
    check_database()
    
    # 2. Kiểm tra endpoint
    check_endpoint()
    
    # 3. Test chức năng đăng ký
    test_register()
    
    print("\n" + "="*60)
    print("TEST HOÀN TẤT")
    print("="*60)
    
    print("\n💡 Nếu có lỗi:")
    print("1. Kiểm tra server có đang chạy không: py manage.py runserver")
    print("2. Kiểm tra database có kết nối được không")
    print("3. Kiểm tra browser console (F12) khi đăng ký trên web")
    print("4. Kiểm tra network tab để xem request/response")
    print()

if __name__ == '__main__':
    main()

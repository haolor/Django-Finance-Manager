"""Test API đăng ký trực tiếp"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()

# Test với data giống như UI
data = {
    'username': 'testnha',
    'email': 'testnha@gmail.com',
    'password': '........',  # 8 dots = 8 chars
    'password_confirm': '........',
    'first_name': 'test',
    'last_name': 'thoi'
}

print("Testing registration with data:")
print(f"  Username: {data['username']}")
print(f"  Email: {data['email']}")
print(f"  Password length: {len(data['password'])} chars")
print(f"  First name: {data['first_name']}")
print(f"  Last name: {data['last_name']}")
print()

response = client.post('/api/auth/register/', data, format='json')

print(f"Status Code: {response.status_code}")
print(f"Response: {response.data}")
print()

if response.status_code == 201:
    print("✅ Registration successful!")
else:
    print("❌ Registration failed!")
    if response.status_code == 400:
        print("\nErrors:")
        for field, errors in response.data.items():
            print(f"  {field}: {errors}")

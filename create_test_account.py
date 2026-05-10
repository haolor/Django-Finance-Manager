#!/usr/bin/env python
"""
Create test account for Django Finance Manager
Run: python create_test_account.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def create_test_account():
    """Create test account with testuser/12312345"""
    username = 'testuser'
    password = '12312345'
    email = 'testuser@example.com'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"✓ Account '{username}' already exists!")
        user = User.objects.get(username=username)
        print(f"  Email: {user.email}")
        print(f"  Created: {user.date_joined}")
        return
    
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Test',
        last_name='User'
    )
    
    print(f"✓ Test account created successfully!")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
    print(f"  Created: {user.date_joined}")

if __name__ == '__main__':
    try:
        create_test_account()
        print("\n✓ Done! You can now login with:")
        print("  Username: testuser")
        print("  Password: 12312345")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

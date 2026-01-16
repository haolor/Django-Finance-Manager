"""Script để tạo dữ liệu mẫu cho các bảng"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from finance.models import Category, Transaction, Budget, SpendingPattern
from django.contrib.auth.models import User
from django.db.models import Sum

def create_sample_data():
    print("=" * 80)
    print("TẠO DỮ LIỆU MẪU")
    print("=" * 80)
    
    # Tạo admin user (superuser)
    print("\n👤 Tạo Admin User...")
    try:
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_created:
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"✅ Đã tạo admin user: {admin_user.username} (password: admin123)")
        else:
            print(f"✅ Admin user đã tồn tại: {admin_user.username}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin user: {e}")
    
    # Lấy hoặc tạo demo user
    print("\n👤 Tạo Demo User...")
    try:
        demo_user, demo_created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
            }
        )
        if demo_created:
            demo_user.set_password('demo123')
            demo_user.save()
            print(f"✅ Đã tạo demo user: {demo_user.username} (password: demo123)")
        else:
            print(f"✅ Demo user đã tồn tại: {demo_user.username}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo demo user: {e}")
    
    # Sử dụng admin user làm user chính để tạo dữ liệu
    user = admin_user
    
    # Lấy các categories
    categories = Category.objects.all()
    if not categories.exists():
        print("❌ Chưa có categories. Hãy chạy: python manage.py init_categories")
        return
    
    expense_categories = categories.filter(type='expense')
    income_categories = categories.filter(type='income')
    
    print(f"\n📁 Tìm thấy {categories.count()} categories")
    print(f"   - Chi tiêu: {expense_categories.count()}")
    print(f"   - Thu nhập: {income_categories.count()}")
    
    # Tạo Transactions cho admin user
    print("\n💰 Tạo Transactions cho Admin User...")
    admin_transactions_data = [
        # Chi tiêu
        {'category': 'Ăn uống', 'amount': 50000, 'description': 'Ăn sáng tại quán cà phê', 'days_ago': 0},
        {'category': 'Ăn uống', 'amount': 120000, 'description': 'Ăn trưa với bạn bè', 'days_ago': 1},
        {'category': 'Di chuyển', 'amount': 35000, 'description': 'Grab đi làm', 'days_ago': 0},
        {'category': 'Di chuyển', 'amount': 25000, 'description': 'Xe bus', 'days_ago': 2},
        {'category': 'Giải trí', 'amount': 200000, 'description': 'Xem phim rạp', 'days_ago': 3},
        {'category': 'Mua sắm', 'amount': 500000, 'description': 'Mua quần áo', 'days_ago': 5},
        {'category': 'Y tế', 'amount': 300000, 'description': 'Khám bệnh', 'days_ago': 7},
        {'category': 'Học tập', 'amount': 250000, 'description': 'Mua sách', 'days_ago': 10},
        {'category': 'Hóa đơn', 'amount': 500000, 'description': 'Tiền điện tháng 1', 'days_ago': 12},
        {'category': 'Hóa đơn', 'amount': 200000, 'description': 'Tiền nước', 'days_ago': 12},
        {'category': 'Ăn uống', 'amount': 80000, 'description': 'Cà phê buổi sáng', 'days_ago': 15},
        {'category': 'Di chuyển', 'amount': 40000, 'description': 'Taxi', 'days_ago': 18},
        {'category': 'Giải trí', 'amount': 150000, 'description': 'Karaoke', 'days_ago': 20},
        {'category': 'Mua sắm', 'amount': 300000, 'description': 'Mua đồ dùng cá nhân', 'days_ago': 22},
        {'category': 'Tiết kiệm', 'amount': 2000000, 'description': 'Gửi tiết kiệm', 'days_ago': 25},
        
        # Thu nhập
        {'category': 'Lương', 'amount': 10000000, 'description': 'Lương tháng 1', 'days_ago': 1},
        {'category': 'Thu nhập kinh doanh', 'amount': 5000000, 'description': 'Bán hàng online', 'days_ago': 5},
        {'category': 'Đầu tư', 'amount': 2000000, 'description': 'Lãi đầu tư', 'days_ago': 10},
        {'category': 'Thu nhập khác', 'amount': 500000, 'description': 'Tiền thưởng', 'days_ago': 15},
    ]
    
    created_admin_transactions = 0
    for data in admin_transactions_data:
        try:
            category = categories.get(name=data['category'])
            transaction_date = date.today() - timedelta(days=data['days_ago'])
            
            # Kiểm tra xem transaction đã tồn tại chưa
            existing = Transaction.objects.filter(
                user=admin_user,
                category=category,
                amount=Decimal(data['amount']),
                transaction_date=transaction_date,
                description=data['description']
            ).first()
            
            if not existing:
                transaction = Transaction.objects.create(
                    user=admin_user,
                    category=category,
                    amount=Decimal(data['amount']),
                    description=data['description'],
                    transaction_date=transaction_date,
                )
                created_admin_transactions += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo transaction: {e}")
    
    print(f"✅ Đã tạo {created_admin_transactions} transactions cho admin user")
    
    # Tạo Transactions cho demo user (nếu chưa có)
    print("\n💰 Tạo Transactions cho Demo User...")
    demo_transactions_data = [
        {'category': 'Ăn uống', 'amount': 60000, 'description': 'Ăn sáng', 'days_ago': 0},
        {'category': 'Di chuyển', 'amount': 30000, 'description': 'Grab', 'days_ago': 1},
        {'category': 'Lương', 'amount': 8000000, 'description': 'Lương tháng 1', 'days_ago': 2},
        {'category': 'Mua sắm', 'amount': 400000, 'description': 'Mua đồ', 'days_ago': 3},
    ]
    
    created_demo_transactions = 0
    for data in demo_transactions_data:
        try:
            category = categories.get(name=data['category'])
            transaction_date = date.today() - timedelta(days=data['days_ago'])
            
            existing = Transaction.objects.filter(
                user=demo_user,
                category=category,
                amount=Decimal(data['amount']),
                transaction_date=transaction_date,
                description=data['description']
            ).first()
            
            if not existing:
                transaction = Transaction.objects.create(
                    user=demo_user,
                    category=category,
                    amount=Decimal(data['amount']),
                    description=data['description'],
                    transaction_date=transaction_date,
                )
                created_demo_transactions += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo transaction: {e}")
    
    print(f"✅ Đã tạo {created_demo_transactions} transactions cho demo user")
    
    # Tạo Budgets cho admin user
    print("\n📊 Tạo Budgets cho Admin User...")
    admin_budgets_data = [
        {'category': 'Ăn uống', 'amount': 2000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Di chuyển', 'amount': 500000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Giải trí', 'amount': 1000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Mua sắm', 'amount': 2000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Y tế', 'amount': 1000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Hóa đơn', 'amount': 1500000, 'period': 'monthly', 'days_ago': 0},
    ]
    
    created_admin_budgets = 0
    for data in admin_budgets_data:
        try:
            category = expense_categories.get(name=data['category'])
            start_date = date.today() - timedelta(days=data['days_ago'])
            end_date = start_date + timedelta(days=30)
            
            existing = Budget.objects.filter(
                user=admin_user,
                category=category,
                start_date=start_date
            ).first()
            
            if not existing:
                budget = Budget.objects.create(
                    user=admin_user,
                    category=category,
                    amount=Decimal(data['amount']),
                    period=data['period'],
                    start_date=start_date,
                    end_date=end_date,
                )
                created_admin_budgets += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo budget: {e}")
    
    print(f"✅ Đã tạo {created_admin_budgets} budgets cho admin user")
    
    # Tạo Budgets cho demo user
    print("\n📊 Tạo Budgets cho Demo User...")
    demo_budgets_data = [
        {'category': 'Ăn uống', 'amount': 1500000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Di chuyển', 'amount': 400000, 'period': 'monthly', 'days_ago': 0},
    ]
    
    created_demo_budgets = 0
    for data in demo_budgets_data:
        try:
            category = expense_categories.get(name=data['category'])
            start_date = date.today() - timedelta(days=data['days_ago'])
            end_date = start_date + timedelta(days=30)
            
            existing = Budget.objects.filter(
                user=demo_user,
                category=category,
                start_date=start_date
            ).first()
            
            if not existing:
                budget = Budget.objects.create(
                    user=demo_user,
                    category=category,
                    amount=Decimal(data['amount']),
                    period=data['period'],
                    start_date=start_date,
                    end_date=end_date,
                )
                created_demo_budgets += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo budget: {e}")
    
    print(f"✅ Đã tạo {created_demo_budgets} budgets cho demo user")
    
    # Cập nhật Spending Patterns cho admin user
    print("\n📈 Cập nhật Spending Patterns cho Admin User...")
    from finance.ai_service import AIService
    try:
        AIService.update_spending_patterns(admin_user)
        admin_patterns = SpendingPattern.objects.filter(user=admin_user)
        print(f"✅ Đã tạo/cập nhật {admin_patterns.count()} spending patterns cho admin user")
    except Exception as e:
        print(f"⚠️  Lỗi khi cập nhật spending patterns cho admin: {e}")
    
    # Cập nhật Spending Patterns cho demo user
    print("\n📈 Cập nhật Spending Patterns cho Demo User...")
    try:
        AIService.update_spending_patterns(demo_user)
        demo_patterns = SpendingPattern.objects.filter(user=demo_user)
        print(f"✅ Đã tạo/cập nhật {demo_patterns.count()} spending patterns cho demo user")
    except Exception as e:
        print(f"⚠️  Lỗi khi cập nhật spending patterns cho demo: {e}")
    
    # Thống kê
    print("\n" + "=" * 80)
    print("📊 THỐNG KÊ SAU KHI TẠO DỮ LIỆU:")
    print("=" * 80)
    
    # Thống kê cho Admin User
    print("\n👤 ADMIN USER:")
    admin_total_transactions = Transaction.objects.filter(user=admin_user).count()
    admin_total_income = Transaction.objects.filter(
        user=admin_user, category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    admin_total_expense = Transaction.objects.filter(
        user=admin_user, category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    print(f"  Tổng số transactions: {admin_total_transactions}")
    print(f"  Tổng thu nhập: {float(admin_total_income):,.0f} ₫")
    print(f"  Tổng chi tiêu: {float(admin_total_expense):,.0f} ₫")
    print(f"  Số dư: {float(admin_total_income - admin_total_expense):,.0f} ₫")
    print(f"  Tổng số budgets: {Budget.objects.filter(user=admin_user).count()}")
    print(f"  Tổng số spending patterns: {SpendingPattern.objects.filter(user=admin_user).count()}")
    
    # Thống kê cho Demo User
    print("\n👤 DEMO USER:")
    demo_total_transactions = Transaction.objects.filter(user=demo_user).count()
    demo_total_income = Transaction.objects.filter(
        user=demo_user, category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    demo_total_expense = Transaction.objects.filter(
        user=demo_user, category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    print(f"  Tổng số transactions: {demo_total_transactions}")
    print(f"  Tổng thu nhập: {float(demo_total_income):,.0f} ₫")
    print(f"  Tổng chi tiêu: {float(demo_total_expense):,.0f} ₫")
    print(f"  Số dư: {float(demo_total_income - demo_total_expense):,.0f} ₫")
    print(f"  Tổng số budgets: {Budget.objects.filter(user=demo_user).count()}")
    print(f"  Tổng số spending patterns: {SpendingPattern.objects.filter(user=demo_user).count()}")
    
    # Thống kê tổng
    print("\n📊 TỔNG QUAN:")
    total_users = User.objects.count()
    total_transactions_all = Transaction.objects.count()
    total_budgets_all = Budget.objects.count()
    total_patterns_all = SpendingPattern.objects.count()
    
    print(f"  Tổng số users: {total_users}")
    print(f"  Tổng số transactions (tất cả users): {total_transactions_all}")
    print(f"  Tổng số budgets (tất cả users): {total_budgets_all}")
    print(f"  Tổng số spending patterns (tất cả users): {total_patterns_all}")
    
    print("\n✅ Hoàn thành tạo dữ liệu mẫu!")
    print("=" * 80)
    print("\n🔑 THÔNG TIN ĐĂNG NHẬP:")
    print(f"  Admin: username='admin', password='admin123'")
    print(f"  Demo: username='demo_user', password='demo123'")
    print("=" * 80)

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


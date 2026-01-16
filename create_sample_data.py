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

def create_sample_data():
    print("=" * 80)
    print("TẠO DỮ LIỆU MẪU")
    print("=" * 80)
    
    # Lấy user đầu tiên (hoặc tạo mới nếu chưa có)
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='demo_user',
                email='demo@example.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
            print(f"✅ Đã tạo user mới: {user.username}")
        else:
            print(f"✅ Sử dụng user: {user.username}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo user: {e}")
        return
    
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
    
    # Tạo Transactions
    print("\n💰 Tạo Transactions...")
    transactions_data = [
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
    
    created_transactions = 0
    for data in transactions_data:
        try:
            category = categories.get(name=data['category'])
            transaction_date = date.today() - timedelta(days=data['days_ago'])
            
            transaction = Transaction.objects.create(
                user=user,
                category=category,
                amount=Decimal(data['amount']),
                description=data['description'],
                transaction_date=transaction_date,
            )
            created_transactions += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo transaction: {e}")
    
    print(f"✅ Đã tạo {created_transactions} transactions")
    
    # Tạo Budgets
    print("\n📊 Tạo Budgets...")
    budgets_data = [
        {'category': 'Ăn uống', 'amount': 2000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Di chuyển', 'amount': 500000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Giải trí', 'amount': 1000000, 'period': 'monthly', 'days_ago': 0},
        {'category': 'Mua sắm', 'amount': 2000000, 'period': 'monthly', 'days_ago': 0},
    ]
    
    created_budgets = 0
    for data in budgets_data:
        try:
            category = expense_categories.get(name=data['category'])
            start_date = date.today() - timedelta(days=data['days_ago'])
            end_date = start_date + timedelta(days=30)
            
            budget = Budget.objects.create(
                user=user,
                category=category,
                amount=Decimal(data['amount']),
                period=data['period'],
                start_date=start_date,
                end_date=end_date,
            )
            created_budgets += 1
        except Category.DoesNotExist:
            print(f"⚠️  Không tìm thấy category: {data['category']}")
        except Exception as e:
            print(f"⚠️  Lỗi khi tạo budget: {e}")
    
    print(f"✅ Đã tạo {created_budgets} budgets")
    
    # Cập nhật Spending Patterns (sẽ được tạo tự động khi chạy AI service)
    print("\n📈 Cập nhật Spending Patterns...")
    from finance.ai_service import AIService
    try:
        AIService.update_spending_patterns(user)
        patterns = SpendingPattern.objects.filter(user=user)
        print(f"✅ Đã tạo/cập nhật {patterns.count()} spending patterns")
    except Exception as e:
        print(f"⚠️  Lỗi khi cập nhật spending patterns: {e}")
    
    # Thống kê
    print("\n" + "=" * 80)
    print("📊 THỐNG KÊ SAU KHI TẠO DỮ LIỆU:")
    print("=" * 80)
    
    total_transactions = Transaction.objects.filter(user=user).count()
    total_income = Transaction.objects.filter(
        user=user, category__type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_expense = Transaction.objects.filter(
        user=user, category__type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    print(f"Tổng số transactions: {total_transactions}")
    print(f"Tổng thu nhập: {float(total_income):,.0f} ₫")
    print(f"Tổng chi tiêu: {float(total_expense):,.0f} ₫")
    print(f"Số dư: {float(total_income - total_expense):,.0f} ₫")
    print(f"Tổng số budgets: {Budget.objects.filter(user=user).count()}")
    print(f"Tổng số spending patterns: {SpendingPattern.objects.filter(user=user).count()}")
    
    print("\n✅ Hoàn thành tạo dữ liệu mẫu!")
    print("=" * 80)

if __name__ == '__main__':
    try:
        from django.db.models import Sum
        create_sample_data()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


"""Script để hiển thị dữ liệu từ các bảng trong database"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from finance.models import Category, Transaction, Budget, SpendingPattern
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q

def print_table_data():
    print("=" * 100)
    print("DỮ LIỆU CÁC BẢNG TRONG DATABASE")
    print("=" * 100)
    
    # Categories
    print("\n📁 BẢNG CATEGORIES:")
    print("-" * 100)
    categories = Category.objects.all().order_by('type', 'name')
    if categories.exists():
        print(f"{'ID':<5} {'Tên':<25} {'Loại':<12} {'Icon':<10} {'Màu':<15} {'Ngày tạo'}")
        print("-" * 100)
        for cat in categories:
            print(f"{cat.id:<5} {cat.name:<25} {cat.type:<12} {cat.icon:<10} {cat.color:<15} {cat.created_at.strftime('%Y-%m-%d')}")
    else:
        print("Chưa có dữ liệu")
    print(f"\nTổng số: {categories.count()} danh mục")
    
    # Users
    print("\n👤 BẢNG USERS:")
    print("-" * 100)
    users = User.objects.all()
    if users.exists():
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Tên đầy đủ':<20} {'Ngày tham gia'}")
        print("-" * 100)
        for user in users:
            full_name = f"{user.first_name} {user.last_name}".strip() or "-"
            date_joined = user.date_joined.strftime('%Y-%m-%d') if user.date_joined else "-"
            print(f"{user.id:<5} {user.username:<20} {user.email or '-':<30} {full_name:<20} {date_joined}")
    else:
        print("Chưa có dữ liệu")
    print(f"\nTổng số: {users.count()} người dùng")
    
    # Transactions
    print("\n💰 BẢNG TRANSACTIONS:")
    print("-" * 100)
    transactions = Transaction.objects.all().select_related('user', 'category').order_by('-transaction_date', '-created_at')[:30]
    if transactions.exists():
        print(f"{'ID':<5} {'User':<12} {'Danh mục':<20} {'Loại':<8} {'Số tiền':<18} {'Ngày':<12} {'Mô tả'}")
        print("-" * 100)
        for trans in transactions:
            category_name = trans.category.name if trans.category else "Không có"
            category_type = trans.category.type if trans.category else "-"
            amount_str = f"{float(trans.amount):,.0f} ₫"
            desc = (trans.description[:25] + "...") if trans.description and len(trans.description) > 25 else (trans.description or "-")
            print(f"{trans.id:<5} {trans.user.username:<12} {category_name:<20} {category_type:<8} {amount_str:<18} {trans.transaction_date.strftime('%Y-%m-%d'):<12} {desc}")
    else:
        print("Chưa có dữ liệu")
    total_transactions = Transaction.objects.count()
    print(f"\nTổng số: {total_transactions} giao dịch (hiển thị 30 đầu tiên)")
    
    # Budgets
    print("\n📊 BẢNG BUDGETS:")
    print("-" * 100)
    budgets = Budget.objects.all().select_related('user', 'category').order_by('-start_date')
    if budgets.exists():
        print(f"{'ID':<5} {'User':<12} {'Danh mục':<20} {'Số tiền':<18} {'Kỳ':<10} {'Bắt đầu':<12} {'Kết thúc':<12}")
        print("-" * 100)
        for budget in budgets:
            category_name = budget.category.name if budget.category else "Không có"
            amount_str = f"{float(budget.amount):,.0f} ₫"
            end_date_str = budget.end_date.strftime('%Y-%m-%d') if budget.end_date else "-"
            print(f"{budget.id:<5} {budget.user.username:<12} {category_name:<20} {amount_str:<18} {budget.period:<10} {budget.start_date.strftime('%Y-%m-%d'):<12} {end_date_str:<12}")
    else:
        print("Chưa có dữ liệu")
    print(f"\nTổng số: {budgets.count()} ngân sách")
    
    # Spending Patterns
    print("\n📈 BẢNG SPENDING PATTERNS:")
    print("-" * 100)
    patterns = SpendingPattern.objects.all().select_related('user', 'category').order_by('-average_amount')
    if patterns.exists():
        print(f"{'ID':<5} {'User':<12} {'Danh mục':<20} {'TB số tiền':<18} {'Tần suất':<10} {'Giao dịch cuối':<15} {'Cập nhật'}")
        print("-" * 100)
        for pattern in patterns:
            category_name = pattern.category.name if pattern.category else "Không có"
            avg_str = f"{float(pattern.average_amount):,.0f} ₫"
            last_trans = pattern.last_transaction_date.strftime('%Y-%m-%d') if pattern.last_transaction_date else "-"
            updated = pattern.updated_at.strftime('%Y-%m-%d') if pattern.updated_at else "-"
            print(f"{pattern.id:<5} {pattern.user.username:<12} {category_name:<20} {avg_str:<18} {pattern.frequency:<10} {last_trans:<15} {updated}")
    else:
        print("Chưa có dữ liệu")
    print(f"\nTổng số: {patterns.count()} mẫu chi tiêu")
    
    # Summary Statistics
    print("\n" + "=" * 100)
    print("📊 THỐNG KÊ TỔNG QUAN:")
    print("=" * 100)
    
    if Transaction.objects.exists():
        total_income = Transaction.objects.filter(category__type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_expense = Transaction.objects.filter(category__type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        income_count = Transaction.objects.filter(category__type='income').count()
        expense_count = Transaction.objects.filter(category__type='expense').count()
        
        print(f"Tổng thu nhập: {float(total_income):,.0f} ₫ ({income_count} giao dịch)")
        print(f"Tổng chi tiêu: {float(total_expense):,.0f} ₫ ({expense_count} giao dịch)")
        print(f"Số dư: {float(total_income - total_expense):,.0f} ₫")
        
        # Top categories by expense
        print("\n🏆 TOP 5 DANH MỤC CHI TIÊU NHIỀU NHẤT:")
        top_expense = Transaction.objects.filter(
            category__type='expense'
        ).values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        for i, item in enumerate(top_expense, 1):
            print(f"  {i}. {item['category__name']}: {float(item['total']):,.0f} ₫ ({item['count']} giao dịch)")
    
    print("\n" + "=" * 100)

if __name__ == '__main__':
    try:
        print_table_data()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()


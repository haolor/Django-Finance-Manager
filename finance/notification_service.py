"""Service để tạo và quản lý notifications"""
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Notification, Transaction, Budget, UserPreferences


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
    
    # TODO: Gửi email nếu send_email=True
    # if send_email:
    #     send_notification_email(notification)
    
    return notification


def check_large_transaction(transaction):
    """Kiểm tra và tạo notification nếu giao dịch lớn"""
    try:
        preferences = UserPreferences.objects.get(user=transaction.user)
        
        if not preferences.notify_large_transaction:
            return
        
        threshold = preferences.large_transaction_threshold
        
        if transaction.amount >= threshold:
            create_notification(
                user=transaction.user,
                notification_type='large_transaction',
                title='Giao dịch lớn được phát hiện',
                message=f'Bạn vừa thực hiện một giao dịch với số tiền {transaction.amount:,.0f} ₫, vượt quá ngưỡng {threshold:,.0f} ₫ của bạn.',
                related_transaction=transaction,
                send_email=preferences.notify_large_transaction
            )
    except UserPreferences.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error checking large transaction: {e}")


def check_budget_exceeded(user, category=None):
    """Kiểm tra và tạo notification nếu vượt ngân sách"""
    try:
        preferences = UserPreferences.objects.get(user=user)
        
        if not preferences.notify_budget_exceeded:
            return
        
        today = timezone.now().date()
        current_month_start = datetime(today.year, today.month, 1).date()
        
        # Lấy tất cả budgets của user trong tháng hiện tại
        budgets = Budget.objects.filter(
            user=user,
            start_date__lte=today,
            category=category if category else None
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )
        
        if category:
            budgets = budgets.filter(category=category)
        
        for budget in budgets:
            # Tính tổng chi tiêu trong period
            if budget.period == 'monthly':
                start_date = current_month_start
                end_date = today
            elif budget.period == 'weekly':
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif budget.period == 'daily':
                start_date = today
                end_date = today
            else:  # yearly
                start_date = datetime(today.year, 1, 1).date()
                end_date = today
            
            # Tính tổng chi tiêu
            total_spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_date__gte=start_date,
                transaction_date__lte=end_date,
                category__type='expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            if total_spent > budget.amount:
                excess = total_spent - budget.amount
                create_notification(
                    user=user,
                    notification_type='budget_exceeded',
                    title=f'Vượt ngân sách: {budget.category.name}',
                    message=f'Bạn đã vượt ngân sách {budget.amount:,.0f} ₫ cho danh mục "{budget.category.name}" với {excess:,.0f} ₫ (tổng chi: {total_spent:,.0f} ₫).',
                    related_budget=budget,
                    send_email=preferences.notify_budget_exceeded
                )
    except UserPreferences.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error checking budget exceeded: {e}")


def create_anomaly_notification(user, anomaly_data):
    """Tạo notification cho anomaly được phát hiện"""
    try:
        preferences = UserPreferences.objects.get(user=user)
        
        if not preferences.notify_anomaly_detected:
            return
        
        transaction = anomaly_data.get('transaction')
        if transaction:
            create_notification(
                user=user,
                notification_type='anomaly_detected',
                title='Phát hiện giao dịch bất thường',
                message=f'Giao dịch {anomaly_data.get("amount", 0):,.0f} ₫ trong danh mục "{anomaly_data.get("category", "Khác")}" có vẻ bất thường so với mẫu chi tiêu thông thường của bạn.',
                related_transaction=transaction,
                send_email=preferences.notify_anomaly_detected
            )
    except UserPreferences.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error creating anomaly notification: {e}")


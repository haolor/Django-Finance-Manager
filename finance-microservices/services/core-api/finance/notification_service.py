"""Service để tạo và quản lý notifications"""
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.mail import send_mail
from django.conf import settings

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

    # Gửi email nếu người dùng bật thông báo email
    if send_email:
        send_notification_email(notification)
    
    return notification



def send_notification_email(notification: Notification) -> bool:
    """Gửi email notification cho người dùng (nếu user có email)."""
    try:
        user = notification.user
        if not getattr(user, "email", None):
            return False

        subject = f'[Finance Manager] {notification.title}'
        # Plain text đơn giản để đảm bảo gửi được ngay (không phụ thuộc template HTML).
        plain_message = (
            f"{notification.title}\n\n"
            f"{notification.message}\n\n"
            f"Loại thông báo: {notification.get_type_display()}\n"
            f"Thời gian: {notification.created_at.strftime('%d/%m/%Y %H:%M')}\n"
        )

        type_colors = {
        'large_transaction': ("#dc3545", "#f8d7da"),
        'budget_exceeded': ("#ffc107", "#fff3cd"),
        'anomaly_detected': ("#17a2b8", "#d1ecf1"),
        }

        color, bg = type_colors.get(notification.type, ("#4CAF50", "#f5f5f5"))
        

        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; border-radius: 10px; overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #4CAF50; color: white; padding: 15px; text-align: center;">
                <h2>💰 Finance Manager</h2>
            </div>

            <!-- Body -->
            <div style="padding: 20px;">
                <h3 style="color: #333;">{notification.title}</h3>
                
                <p style="font-size: 16px; color: #555;">
                    {notification.message}
                </p>

                <!-- Highlight box -->
                <div style="background: {bg}; padding: 15px; border-left: 5px solid {color}; border-radius: 8px; margin-top: 15px;">
                    <p style="margin: 0;"><strong>📌 Loại:</strong> {notification.get_type_display()}</p>
                    <p style="margin: 0;"><strong>⏰ Thời gian:</strong> {notification.created_at.strftime('%d/%m/%Y %H:%M')}</p>
                </div>

            </div>

            <!-- Footer -->
            <div style="background: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #888;">
                Đây là email tự động, vui lòng không trả lời.
            </div>

        </div>
        """


        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )

        notification.email_sent = True
        notification.save(update_fields=["email_sent"])
        return True
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False


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


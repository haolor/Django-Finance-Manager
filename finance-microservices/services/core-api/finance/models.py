from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


def default_list():
    return []


class Category(models.Model):
    """Danh mục giao dịch"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='💰')
    color = models.CharField(max_length=20, default='#3B82F6')
    
    # Phân loại: income (thu) hoặc expense (chi)
    type = models.CharField(
        max_length=10,
        choices=[('income', 'Thu nhập'), ('expense', 'Chi tiêu')],
        default='expense'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Giao dịch thu chi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    description = models.TextField(blank=True)
    transaction_date = models.DateField()
    
    # Lưu thông tin từ NLP nếu có
    original_nlp_input = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_date}"


class Budget(models.Model):
    """Ngân sách theo danh mục"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Hàng ngày'),
            ('weekly', 'Hàng tuần'),
            ('monthly', 'Hàng tháng'),
            ('yearly', 'Hàng năm')
        ],
        default='monthly'
    )
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.amount}"


class SpendingPattern(models.Model):
    """Mẫu chi tiêu để phân tích AI"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spending_patterns')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='spending_patterns')
    
    average_amount = models.DecimalField(max_digits=15, decimal_places=2)
    frequency = models.IntegerField(default=0)  # Số lần trong tháng
    last_transaction_date = models.DateField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - Pattern"


class UserPreferences(models.Model):
    """Cài đặt giao diện và báo cáo của người dùng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Theme settings
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Sáng'),
            ('dark', 'Tối'),
            ('auto', 'Tự động'),
        ],
        default='light'
    )
    primary_color = models.CharField(max_length=20, default='#3B82F6')  # Màu chủ đạo
    sidebar_collapsed = models.BooleanField(default=False)
    
    # Report preferences
    default_report_period = models.CharField(
        max_length=20,
        choices=[
            ('week', 'Tuần'),
            ('month', 'Tháng'),
            ('quarter', 'Quý'),
            ('year', 'Năm'),
        ],
        default='month'
    )
    report_categories = models.JSONField(default=default_list, blank=True)  # Danh sách categories muốn xem trong báo cáo
    report_include_charts = models.BooleanField(default=True)
    report_include_tables = models.BooleanField(default=True)
    report_email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Không gửi'),
            ('daily', 'Hàng ngày'),
            ('weekly', 'Hàng tuần'),
            ('monthly', 'Hàng tháng'),
        ],
        default='never'
    )
    
    # Notification preferences
    notify_budget_exceeded = models.BooleanField(default=True)
    notify_large_transaction = models.BooleanField(default=True)
    notify_anomaly_detected = models.BooleanField(default=True)
    large_transaction_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=1000000)
    
    # Dashboard preferences
    dashboard_widgets = models.JSONField(default=default_list, blank=True)  # Widgets hiển thị trên dashboard
    dashboard_chart_type = models.CharField(
        max_length=20,
        choices=[
            ('line', 'Đường'),
            ('bar', 'Cột'),
            ('pie', 'Tròn'),
        ],
        default='line'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"{self.user.username} - Preferences"


class Notification(models.Model):
    """Thông báo cho người dùng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    NOTIFICATION_TYPES = [
        ('budget_exceeded', 'Vượt ngân sách'),
        ('large_transaction', 'Giao dịch lớn'),
        ('anomaly_detected', 'Phát hiện bất thường'),
        ('report_ready', 'Báo cáo sẵn sàng'),
        ('system', 'Hệ thống'),
    ]
    
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    
    # Metadata để liên kết với transaction, budget, etc.
    related_transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    related_budget = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.created_at}"
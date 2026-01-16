from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


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


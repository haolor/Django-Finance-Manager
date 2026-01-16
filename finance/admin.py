from django.contrib import admin
from .models import Category, Transaction, Budget, SpendingPattern


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'icon', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'transaction_date', 'created_at']
    list_filter = ['transaction_date', 'category', 'created_at']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'transaction_date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'period', 'start_date']
    list_filter = ['period', 'start_date']
    search_fields = ['user__username', 'category__name']


@admin.register(SpendingPattern)
class SpendingPatternAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'average_amount', 'frequency', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'category__name']


"""
Management command để tạo các danh mục mặc định
"""
from django.core.management.base import BaseCommand
from finance.models import Category


class Command(BaseCommand):
    help = 'Tạo các danh mục mặc định cho hệ thống'

    def handle(self, *args, **options):
        categories = [
            # Chi tiêu
            {'name': 'Ăn uống', 'type': 'expense', 'icon': '🍔', 'color': '#EF4444'},
            {'name': 'Di chuyển', 'type': 'expense', 'icon': '🚗', 'color': '#3B82F6'},
            {'name': 'Giải trí', 'type': 'expense', 'icon': '🎬', 'color': '#8B5CF6'},
            {'name': 'Mua sắm', 'type': 'expense', 'icon': '🛍️', 'color': '#EC4899'},
            {'name': 'Y tế', 'type': 'expense', 'icon': '🏥', 'color': '#10B981'},
            {'name': 'Học tập', 'type': 'expense', 'icon': '📚', 'color': '#F59E0B'},
            {'name': 'Tiết kiệm', 'type': 'expense', 'icon': '💰', 'color': '#14B8A6'},
            {'name': 'Hóa đơn', 'type': 'expense', 'icon': '📄', 'color': '#6366F1'},
            {'name': 'Khác', 'type': 'expense', 'icon': '📦', 'color': '#6B7280'},
            
            # Thu nhập
            {'name': 'Lương', 'type': 'income', 'icon': '💵', 'color': '#10B981'},
            {'name': 'Thu nhập kinh doanh', 'type': 'income', 'icon': '💼', 'color': '#10B981'},
            {'name': 'Đầu tư', 'type': 'income', 'icon': '📈', 'color': '#10B981'},
            {'name': 'Thu nhập khác', 'type': 'income', 'icon': '💳', 'color': '#10B981'},
        ]
        
        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Đã tạo danh mục: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Danh mục đã tồn tại: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nHoàn thành! Đã tạo {created_count} danh mục mới.')
        )


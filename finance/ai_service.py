"""
AI Service for trend analysis, predictions, and anomaly detection
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Sum, Avg, Count, Q
from django.contrib.auth.models import User
from .models import Transaction, Category, SpendingPattern


class AIService:
    """Service để phân tích AI cho hệ thống tài chính"""
    
    @staticmethod
    def analyze_spending_trends(user: User, days: int = 30) -> Dict:
        """
        Phân tích xu hướng chi tiêu
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        
        # Tính toán theo tuần
        weekly_data = []
        current_date = start_date
        while current_date <= end_date:
            week_start = current_date
            week_end = min(current_date + timedelta(days=6), end_date)
            
            week_transactions = transactions.filter(
                transaction_date__gte=week_start,
                transaction_date__lte=week_end
            )
            
            total_expense = week_transactions.filter(
                category__type='expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            total_income = week_transactions.filter(
                category__type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            weekly_data.append({
                'week': week_start.strftime('%Y-%m-%d'),
                'expense': float(total_expense),
                'income': float(total_income),
                'balance': float(total_income - total_expense),
            })
            
            current_date = week_end + timedelta(days=1)
        
        # Tính xu hướng
        if len(weekly_data) >= 2:
            first_half = weekly_data[:len(weekly_data)//2]
            second_half = weekly_data[len(weekly_data)//2:]
            
            first_avg = sum(d['expense'] for d in first_half) / len(first_half)
            second_avg = sum(d['expense'] for d in second_half) / len(second_half)
            
            trend = 'increasing' if second_avg > first_avg else 'decreasing'
            trend_percentage = abs((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        else:
            trend = 'stable'
            trend_percentage = 0
        
        return {
            'weekly_data': weekly_data,
            'trend': trend,
            'trend_percentage': round(trend_percentage, 2),
            'average_daily_expense': float(sum(d['expense'] for d in weekly_data) / len(weekly_data)) if weekly_data else 0,
        }
    
    @staticmethod
    def predict_next_month_spending(user: User) -> Dict:
        """
        Dự đoán chi tiêu tháng tiếp theo
        """
        # Lấy dữ liệu 3 tháng gần nhất
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='expense'
        )
        
        # Tính trung bình theo tháng
        monthly_totals = []
        current_date = start_date
        while current_date <= end_date:
            month_start = datetime(current_date.year, current_date.month, 1).date()
            if month_start.month == 12:
                month_end = datetime(month_start.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(month_start.year, month_start.month + 1, 1).date() - timedelta(days=1)
            
            month_total = transactions.filter(
                transaction_date__gte=month_start,
                transaction_date__lte=min(month_end, end_date)
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            monthly_totals.append(float(month_total))
            current_date = month_end + timedelta(days=1)
        
        if monthly_totals:
            predicted = sum(monthly_totals) / len(monthly_totals)
        else:
            predicted = 0
        
        return {
            'predicted_amount': round(predicted, 2),
            'confidence': 'medium' if len(monthly_totals) >= 2 else 'low',
            'based_on_months': len(monthly_totals),
        }
    
    @staticmethod
    def detect_anomalies(user: User, days: int = 30) -> List[Dict]:
        """
        Phát hiện bất thường trong chi tiêu
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='expense'
        )
        
        # Tính trung bình và độ lệch chuẩn
        amounts = [float(t.amount) for t in transactions]
        if not amounts:
            return []
        
        mean = sum(amounts) / len(amounts)
        variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        # Phát hiện giao dịch bất thường (vượt quá 2 độ lệch chuẩn)
        threshold = mean + 2 * std_dev
        anomalies = []
        
        for transaction in transactions:
            if float(transaction.amount) > threshold:
                anomalies.append({
                    'id': transaction.id,
                    'amount': float(transaction.amount),
                    'category': transaction.category.name if transaction.category else 'Unknown',
                    'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                    'description': transaction.description,
                    'deviation': round((float(transaction.amount) - mean) / std_dev, 2) if std_dev > 0 else 0,
                })
        
        return sorted(anomalies, key=lambda x: x['amount'], reverse=True)
    
    @staticmethod
    def suggest_savings_plan(user: User) -> Dict:
        """
        Gợi ý kế hoạch tiết kiệm
        """
        # Phân tích chi tiêu theo danh mục
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='expense'
        )
        
        category_totals = transactions.values('category__name').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        total_expense = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        suggestions = []
        for item in category_totals[:5]:  # Top 5 danh mục chi tiêu nhiều nhất
            category_name = item['category__name']
            category_total = float(item['total'])
            percentage = (category_total / float(total_expense) * 100) if total_expense > 0 else 0
            
            if percentage > 30:  # Nếu chi tiêu > 30% tổng chi
                suggestions.append({
                    'category': category_name,
                    'current_spending': category_total,
                    'percentage': round(percentage, 2),
                    'suggestion': f'Cân nhắc giảm chi tiêu cho {category_name}',
                    'potential_savings': round(category_total * 0.1, 2),  # Có thể tiết kiệm 10%
                })
        
        # Tính tổng có thể tiết kiệm
        total_potential_savings = sum(s['potential_savings'] for s in suggestions)
        
        return {
            'suggestions': suggestions,
            'total_potential_savings': round(total_potential_savings, 2),
            'monthly_expense': float(total_expense),
        }
    
    @staticmethod
    def update_spending_patterns(user: User):
        """
        Cập nhật mẫu chi tiêu cho phân tích
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='expense'
        )
        
        # Tính toán mẫu cho mỗi category
        category_stats = transactions.values('category').annotate(
            avg_amount=Avg('amount'),
            frequency=Count('id')
        )
        
        for stat in category_stats:
            if stat['category']:
                category = Category.objects.get(id=stat['category'])
                last_transaction = transactions.filter(
                    category=category
                ).order_by('-transaction_date').first()
                
                SpendingPattern.objects.update_or_create(
                    user=user,
                    category=category,
                    defaults={
                        'average_amount': stat['avg_amount'],
                        'frequency': stat['frequency'],
                        'last_transaction_date': last_transaction.transaction_date if last_transaction else None,
                    }
                )


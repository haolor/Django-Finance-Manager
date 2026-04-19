"""
AI Service for trend analysis, predictions, and anomaly detection
"""
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Sum, Avg, Count, Q
from django.contrib.auth.models import User
from .models import Transaction, Category, SpendingPattern


class AIService:
    """Service để phân tích AI cho hệ thống tài chính"""
    
    @staticmethod
    def analyze_spending_trends(
        user: User,
        days: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Phân tích xu hướng chi tiêu
        """
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
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
    def predict_next_month_spending(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Dự đoán chi tiêu tháng tiếp theo
        """
        if end_date is None:
            end_date = datetime.now().date()
        # Mặc định lấy dữ liệu 3 tháng gần nhất
        if start_date is None:
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
    def detect_anomalies(
        user: User,
        days: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Phát hiện bất thường trong chi tiêu
        """
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
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
                    'category_icon': transaction.category.icon if transaction.category else '💰',
                    'date': transaction.transaction_date.strftime('%d/%m/%Y'),
                    'description': transaction.description or 'Không có mô tả',
                    'deviation': round((float(transaction.amount) - mean) / std_dev, 2) if std_dev > 0 else 0,
                    'avg_amount': round(mean, 2),  # Số tiền trung bình để so sánh
                })
        
        return sorted(anomalies, key=lambda x: x['amount'], reverse=True)
    
    @staticmethod
    def suggest_savings_plan(
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Gợi ý kế hoạch tiết kiệm chi tiết và cụ thể
        """
        # Phân tích chi tiêu theo danh mục (30 ngày gần nhất)
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='expense'
        )
        
        # Lấy tổng thu nhập
        income_transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
            category__type='income'
        )
        total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        category_totals = transactions.values('category__name', 'category__id').annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg_amount=Avg('amount')
        ).order_by('-total')
        
        total_expense = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Lấy budgets để so sánh
        from .models import Budget
        budgets = Budget.objects.filter(
            user=user,
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        budget_dict = {b.category_id: b.amount for b in budgets}
        
        suggestions = []
        category_specific_tips = {
            'Ăn uống': [
                'Nấu ăn tại nhà thay vì ăn ngoài 2-3 lần/tuần',
                'Lập danh sách mua sắm trước khi đi chợ/siêu thị',
                'Tận dụng khuyến mãi và mua số lượng lớn cho đồ khô',
                'Hạn chế đặt đồ ăn online, tự nấu sẽ tiết kiệm 30-50%'
            ],
            'Di chuyển': [
                'Sử dụng phương tiện công cộng thay vì taxi/grab',
                'Đi bộ hoặc xe đạp cho quãng đường ngắn',
                'Sử dụng ứng dụng chia sẻ xe để giảm chi phí',
                'Lên kế hoạch lộ trình để tránh đi lại không cần thiết'
            ],
            'Giải trí': [
                'Tìm các hoạt động miễn phí trong khu vực',
                'Sử dụng thẻ thành viên để được giảm giá',
                'Hạn chế xem phim rạp, xem tại nhà hoặc chờ phim cũ',
                'Tổ chức các buổi tụ tập tại nhà thay vì ra ngoài'
            ],
            'Mua sắm': [
                'Mua sắm theo nhu cầu thực sự, tránh mua theo cảm xúc',
                'So sánh giá trước khi mua, đợi sale nếu không gấp',
                'Mua đồ chất lượng tốt một lần thay vì mua rẻ nhiều lần',
                'Bán lại đồ không dùng đến trên các sàn thương mại điện tử'
            ],
            'Y tế': [
                'Khám sức khỏe định kỳ để phát hiện sớm, tránh chi phí lớn',
                'Mua bảo hiểm y tế để được hỗ trợ chi phí',
                'Tập thể dục đều đặn để phòng bệnh',
                'So sánh giá thuốc ở nhiều nhà thuốc khác nhau'
            ],
            'Hóa đơn': [
                'Tắt các thiết bị điện khi không sử dụng',
                'Sử dụng bóng đèn LED tiết kiệm điện',
                'Kiểm tra và sửa chữa rò rỉ nước',
                'Đàm phán lại gói cước internet/điện thoại phù hợp'
            ],
        }
        
        # Loại bỏ các category không nên cắt giảm
        exclude_categories = ['Tiết kiệm', 'Đầu tư']  # Các category này không nên được gợi ý cắt giảm
        
        for item in category_totals[:6]:  # Top 6 danh mục
            category_name = item['category__name']
            
            # Bỏ qua các category không nên cắt giảm
            if category_name in exclude_categories:
                continue
                
            category_id = item['category__id']
            category_total = float(item['total'])
            category_count = item['count']
            avg_amount = float(item['avg_amount'])
            percentage = (category_total / float(total_expense) * 100) if total_expense > 0 else 0
            
            # Tính toán mức độ ưu tiên
            priority_score = 0
            reasons = []
            
            # Kiểm tra vượt budget
            if category_id in budget_dict:
                budget_amount = float(budget_dict[category_id])
                if category_total > budget_amount:
                    priority_score += 3
                    reasons.append(f'Đã vượt budget {((category_total - budget_amount) / budget_amount * 100):.1f}%')
                    potential_savings = round((category_total - budget_amount) * 0.5, 2)  # Tiết kiệm 50% phần vượt
                else:
                    potential_savings = round(category_total * 0.15, 2)  # Tiết kiệm 15% nếu trong budget
            else:
                potential_savings = round(category_total * 0.2, 2)  # Tiết kiệm 20% nếu không có budget
            
            # Chiếm tỷ lệ cao
            if percentage > 30:
                priority_score += 2
                reasons.append(f'Chiếm {percentage:.1f}% tổng chi tiêu')
            elif percentage > 20:
                priority_score += 1
                reasons.append(f'Chiếm {percentage:.1f}% tổng chi tiêu')
            
            # Tần suất chi tiêu cao
            if category_count > 10:
                priority_score += 1
                reasons.append(f'Chi tiêu {category_count} lần trong tháng')
            
            # Số tiền trung bình lớn
            if avg_amount > float(total_expense) * 0.1:
                priority_score += 1
                reasons.append(f'Mỗi lần chi trung bình {avg_amount:,.0f}₫')
            
            # Chỉ thêm gợi ý nếu có tiềm năng tiết kiệm đáng kể
            if potential_savings > 50000 or priority_score >= 2:  # Ít nhất 50k hoặc priority cao
                # Lấy tips cụ thể cho category
                tips = category_specific_tips.get(category_name, [
                    f'Xem xét giảm chi tiêu cho {category_name}',
                    f'Lập kế hoạch chi tiêu cho {category_name}',
                    f'So sánh giá trước khi mua',
                    f'Đặt mục tiêu giảm 10-20% chi tiêu cho {category_name}'
                ])
                
                # Đảm bảo luôn có ít nhất 3 tips
                if len(tips) < 3:
                    tips.extend([
                        f'Lập kế hoạch chi tiêu cho {category_name}',
                        f'So sánh giá trước khi mua'
                    ])
                
                suggestions.append({
                    'category': category_name,
                    'current_spending': category_total,
                    'percentage': round(percentage, 2),
                    'count': category_count,
                    'avg_amount': round(avg_amount, 2),
                    'priority_score': priority_score,
                    'reasons': reasons if reasons else [f'Chiếm {percentage:.1f}% tổng chi tiêu'],
                    'suggestion': f'Có thể tiết kiệm {potential_savings:,.0f}₫/tháng cho {category_name}',
                    'actionable_tips': tips[:3],  # Top 3 tips - đảm bảo luôn có
                    'potential_savings': round(potential_savings, 2),
                })
        
        # Sắp xếp theo priority score
        suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Tính tổng có thể tiết kiệm
        total_potential_savings = sum(s['potential_savings'] for s in suggestions)
        
        # Tính tỷ lệ tiết kiệm so với thu nhập
        savings_rate = (total_potential_savings / float(total_income) * 100) if total_income > 0 else 0
        
        # Gợi ý tổng quan
        overall_recommendation = []
        if total_expense > float(total_income) * 0.8:
            overall_recommendation.append('⚠️ Chi tiêu của bạn đang chiếm hơn 80% thu nhập. Nên cắt giảm ngay!')
        elif total_expense > float(total_income) * 0.6:
            overall_recommendation.append('💡 Chi tiêu đang ở mức cao. Có thể cải thiện để tăng tiết kiệm.')
        
        if savings_rate > 10:
            overall_recommendation.append(f'✅ Nếu thực hiện các gợi ý, bạn có thể tiết kiệm thêm {savings_rate:.1f}% thu nhập mỗi tháng!')
        
        if not suggestions:
            overall_recommendation.append('👍 Chi tiêu của bạn đang hợp lý! Hãy tiếp tục duy trì.')
        
        return {
            'suggestions': suggestions,
            'total_potential_savings': round(total_potential_savings, 2),
            'monthly_expense': float(total_expense),
            'monthly_income': float(total_income),
            'savings_rate': round(savings_rate, 2),
            'overall_recommendation': overall_recommendation,
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


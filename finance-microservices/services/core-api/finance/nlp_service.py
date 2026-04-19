"""
NLP Service for processing natural language input and queries
"""
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional, Tuple, List
from .models import Category


class NLPService:
    """Service để xử lý ngôn ngữ tự nhiên cho hệ thống tài chính"""
    
    # Từ khóa cho các danh mục phổ biến
    CATEGORY_KEYWORDS = {
        'ăn uống': ['ăn', 'uống', 'cơm', 'phở', 'bún', 'cà phê', 'trà', 'nước', 'sáng', 'trưa', 'tối', 'bữa', 'nhà hàng', 'quán'],
        'di chuyển': ['xe', 'taxi', 'grab', 'uber', 'xăng', 'dầu', 'xe bus', 'tàu', 'máy bay', 'đi lại', 'di chuyển'],
        'giải trí': ['xem phim', 'game', 'chơi', 'giải trí', 'karaoke', 'bar', 'club', 'sở thú', 'công viên'],
        'mua sắm': ['mua', 'sắm', 'quần áo', 'giày dép', 'đồ', 'hàng'],
        'y tế': ['bác sĩ', 'bệnh viện', 'thuốc', 'khám', 'y tế', 'sức khỏe'],
        'học tập': ['học', 'sách', 'khóa học', 'trường', 'học phí'],
        'tiết kiệm': ['tiết kiệm', 'gửi tiết kiệm', 'đầu tư'],
        'lương': ['lương', 'thu nhập', 'tiền lương'],
        'kinh doanh': ['bán', 'kinh doanh', 'doanh thu'],
    }
    
    # Mapping từ khóa sang category name
    KEYWORD_TO_CATEGORY = {
        'ăn uống': 'Ăn uống',
        'di chuyển': 'Di chuyển',
        'giải trí': 'Giải trí',
        'mua sắm': 'Mua sắm',
        'y tế': 'Y tế',
        'học tập': 'Học tập',
        'tiết kiệm': 'Tiết kiệm',
        'lương': 'Lương',
        'kinh doanh': 'Thu nhập kinh doanh',
    }
    
    @staticmethod
    def extract_transaction_info(text: str) -> Dict:
        """
        Trích xuất thông tin giao dịch từ câu nhập liệu tự nhiên
        Ví dụ: "Hôm nay chi 50k ăn sáng" -> {amount: 50000, category: "Ăn uống", date: today}
        """
        text = text.lower().strip()
        result = {
            'amount': None,
            'category': None,
            'description': text,
            'date': datetime.now().date(),
            'type': 'expense'  # Mặc định là chi tiêu
        }
        
        # Tìm số tiền (50k, 100000, 50.000đ, etc.)
        amount_patterns = [
            (r'(\d+(?:\.\d+)?)\s*triệu\b', 1000000),  # 1 triệu = 1,000,000
            (r'(\d+(?:\.\d+)?)\s*k\b', 1000),  # 50k = 50,000
            (r'(\d+(?:\.\d+)?)\s*ngàn\b', 1000),  # 50 ngàn = 50,000
            (r'(\d+(?:\.\d+)?)\s*nghìn\b', 1000),  # 50 nghìn = 50,000
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*đ\b', 1),  # 50.000đ hoặc 50,000đ
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*đồng\b', 1),  # 50.000 đồng
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*vnd\b', 1),  # 50.000 vnd
            (r'(\d+(?:\.\d+)?)\s*đ\b', 1),  # 50000đ
            (r'(\d+(?:\.\d+)?)\s*đồng\b', 1),  # 50000 đồng
        ]
        
        found_amounts = []
        for pattern, multiplier in amount_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                value_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    value = float(value_str) * multiplier
                    found_amounts.append((value, match.start()))
                except ValueError:
                    continue
        
        # Lấy số tiền lớn nhất (thường là số tiền chính)
        if found_amounts:
            found_amounts.sort(key=lambda x: x[0], reverse=True)
            result['amount'] = Decimal(str(int(found_amounts[0][0])))
        
        # Nếu không tìm thấy số tiền với pattern, tìm số nguyên lớn nhất
        if result['amount'] is None:
            number_matches = re.finditer(r'\b(\d{4,})\b', text)  # Tìm số có ít nhất 4 chữ số
            amounts = []
            for match in number_matches:
                try:
                    value = float(match.group(1))
                    amounts.append(value)
                except ValueError:
                    continue
            
            if amounts:
                result['amount'] = Decimal(str(int(max(amounts))))
            else:
                # Tìm bất kỳ số nào
                number_match = re.search(r'\b(\d+(?:\.\d+)?)\b', text)
                if number_match:
                    result['amount'] = Decimal(number_match.group(1))
        
        # Xác định loại giao dịch (thu hoặc chi)
        income_keywords = ['thu', 'nhận', 'lương', 'kiếm', 'bán', 'doanh thu']
        expense_keywords = ['chi', 'tiêu', 'mua', 'trả', 'thanh toán']
        
        if any(keyword in text for keyword in income_keywords):
            result['type'] = 'income'
        elif any(keyword in text for keyword in expense_keywords):
            result['type'] = 'expense'
        
        # Tìm danh mục (ưu tiên match dài hơn)
        category_matches = []
        for keyword_group, category_name in NLPService.KEYWORD_TO_CATEGORY.items():
            keywords = NLPService.CATEGORY_KEYWORDS.get(keyword_group, [])
            for keyword in keywords:
                if keyword in text:
                    category_matches.append((len(keyword), category_name))
                    break
        
        if category_matches:
            # Chọn category có keyword dài nhất (match chính xác hơn)
            category_matches.sort(key=lambda x: x[0], reverse=True)
            result['category'] = category_matches[0][1]
        
        # Xác định ngày tháng
        date_patterns = {
            'hôm nay': datetime.now().date(),
            'hôm qua': (datetime.now() - timedelta(days=1)).date(),
            'ngày mai': (datetime.now() + timedelta(days=1)).date(),
        }
        
        for pattern, date_value in date_patterns.items():
            if pattern in text:
                result['date'] = date_value
                break
        
        return result
    
    @staticmethod
    def parse_query(text: str) -> Dict:
        """
        Phân tích câu truy vấn tự nhiên
        Ví dụ: "Tôi đã chi bao nhiêu cho cà phê trong tháng 12?"
        """
        text = text.lower().strip()
        result = {
            'type': 'query',
            'category': None,
            'time_period': None,
            'query_type': 'sum',  # sum, count, average, etc.
        }
        
        # Tìm danh mục trong câu hỏi
        for keyword_group, category_name in NLPService.KEYWORD_TO_CATEGORY.items():
            keywords = NLPService.CATEGORY_KEYWORDS.get(keyword_group, [])
            if any(keyword in text for keyword in keywords):
                result['category'] = category_name
                break
        
        # Tìm khoảng thời gian
        if 'tháng này' in text or 'tháng hiện tại' in text:
            # Tháng hiện tại
            today = datetime.now().date()
            month_start = datetime(today.year, today.month, 1).date()
            if today.month == 12:
                month_end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
            result['time_period'] = {
                'start': month_start,
                'end': month_end,
            }
        elif 'tháng' in text:
            month_match = re.search(r'tháng\s*(\d+)', text)
            if month_match:
                month = int(month_match.group(1))
                current_year = datetime.now().year
                if month == 12:
                    month_end = datetime(current_year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    month_end = datetime(current_year, month + 1, 1).date() - timedelta(days=1)
                result['time_period'] = {
                    'start': datetime(current_year, month, 1).date(),
                    'end': month_end,
                }
        
        if 'tuần' in text or 'week' in text:
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            result['time_period'] = {
                'start': start_of_week,
                'end': today,
            }
        
        if 'năm' in text:
            current_year = datetime.now().year
            result['time_period'] = {
                'start': datetime(current_year, 1, 1).date(),
                'end': datetime(current_year, 12, 31).date(),
            }
        
        # Xác định loại truy vấn
        if 'bao nhiêu' in text or 'tổng' in text:
            result['query_type'] = 'sum'
        elif 'bao nhiêu lần' in text or 'mấy lần' in text:
            result['query_type'] = 'count'
        elif 'trung bình' in text or 'average' in text:
            result['query_type'] = 'average'
        
        return result
    
    @staticmethod
    def get_or_create_category(name: str, category_type: str = 'expense') -> Category:
        """Lấy hoặc tạo category"""
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'type': category_type,
                'icon': '💰',
                'color': '#3B82F6'
            }
        )
        return category


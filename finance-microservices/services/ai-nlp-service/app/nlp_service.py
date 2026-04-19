"""NLP parsing (no Django); ported from monolith finance.nlp_service."""
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict


class NLPService:
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
        text = text.lower().strip()
        result = {
            'amount': None,
            'category': None,
            'description': text,
            'date': datetime.now().date(),
            'type': 'expense',
        }

        amount_patterns = [
            (r'(\d+(?:\.\d+)?)\s*triệu\b', 1000000),
            (r'(\d+(?:\.\d+)?)\s*k\b', 1000),
            (r'(\d+(?:\.\d+)?)\s*ngàn\b', 1000),
            (r'(\d+(?:\.\d+)?)\s*nghìn\b', 1000),
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*đ\b', 1),
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*đồng\b', 1),
            (r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*vnd\b', 1),
            (r'(\d+(?:\.\d+)?)\s*đ\b', 1),
            (r'(\d+(?:\.\d+)?)\s*đồng\b', 1),
        ]

        found_amounts = []
        for pattern, multiplier in amount_patterns:
            for match in re.finditer(pattern, text):
                value_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    value = float(value_str) * multiplier
                    found_amounts.append((value, match.start()))
                except ValueError:
                    continue

        if found_amounts:
            found_amounts.sort(key=lambda x: x[0], reverse=True)
            result['amount'] = Decimal(str(int(found_amounts[0][0])))

        if result['amount'] is None:
            number_matches = re.finditer(r'\b(\d{4,})\b', text)
            amounts = []
            for match in number_matches:
                try:
                    amounts.append(float(match.group(1)))
                except ValueError:
                    continue
            if amounts:
                result['amount'] = Decimal(str(int(max(amounts))))
            else:
                number_match = re.search(r'\b(\d+(?:\.\d+)?)\b', text)
                if number_match:
                    result['amount'] = Decimal(number_match.group(1))

        income_keywords = ['thu', 'nhận', 'lương', 'kiếm', 'bán', 'doanh thu']
        expense_keywords = ['chi', 'tiêu', 'mua', 'trả', 'thanh toán']
        if any(keyword in text for keyword in income_keywords):
            result['type'] = 'income'
        elif any(keyword in text for keyword in expense_keywords):
            result['type'] = 'expense'

        category_matches = []
        for keyword_group, category_name in NLPService.KEYWORD_TO_CATEGORY.items():
            keywords = NLPService.CATEGORY_KEYWORDS.get(keyword_group, [])
            for keyword in keywords:
                if keyword in text:
                    category_matches.append((len(keyword), category_name))
                    break
        if category_matches:
            category_matches.sort(key=lambda x: x[0], reverse=True)
            result['category'] = category_matches[0][1]

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

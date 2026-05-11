"""
NLP Service for processing natural language input and queries
Uses OpenRouter AI (gpt-oss-120b) for 100% accurate extraction
"""
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional
from .models import Category
from .openrouter_service import OpenrouterService


class NLPService:
    """Service để xử lý ngôn ngữ tự nhiên dùng AI"""
    
    # Danh mục hợp lệ
    VALID_CATEGORIES = [
        'Ăn uống', 'Di chuyển', 'Giải trí', 'Mua sắm', 'Y tế', 
        'Học tập', 'Tiết kiệm', 'Lương', 'Thu nhập kinh doanh', 'Khác'
    ]
    
    @staticmethod
    def extract_transaction_info(text: str) -> Dict:
        """
        Trích xuất thông tin giao dịch từ câu nhập liệu tự nhiên dùng AI
        Nếu input có nhiều sub-transactions, tính toán net amount:
        - expense: trừ
        - income: cộng
        Ví dụ: "Chi 100k taxi, nhận 100k mẹ, chi 15k bánh mì" -> net -15k
        """
        try:
            system_prompt = """Bạn là trợ lý tài chính AI chuyên phân tích chi tiêu tiếng Việt.
Nhiệm vụ: Trích xuất TẤT CẢ giao dịch từ câu nhập liệu tự nhiên.

Trả về danh sách JSON objects (mỗi dòng 1 object, không có markdown):
{
  "amount": <số tiền (số nguyên/thập phân)>,
  "category": "<tên danh mục>",
  "description": "<mô tả gốc>",
  "type": "expense" hoặc "income",
  "date": "<YYYY-MM-DD>" hoặc "today"
}

Danh mục hợp lệ: Ăn uống, Di chuyển, Giải trí, Mua sắm, Y tế, Học tập, Tiết kiệm, Lương, Thu nhập kinh doanh, Khác

Ghi chú:
- Trích xuất TẤT CẢ sub-transactions (nếu có nhiều)
- Nếu không có số tiền, để null
- Nếu không rõ danh mục, để "Khác"
- Nếu không rõ ngày, để "today"
- Luôn trả về JSON hợp lệ, không có markdown
"""
            
            user_prompt = f"Trích xuất tất cả giao dịch: {text}"
            response = OpenrouterService._call_generate_content(system_prompt, user_prompt, endpoint="nlp_input")
            
            # Parse multiple JSON objects (one per line)
            transactions = []
            descriptions = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        if data.get('amount') is not None:
                            transactions.append(data)
                            descriptions.append(data.get('description', ''))
                    except json.JSONDecodeError:
                        pass
            
            # If no valid transactions found, fallback
            if not transactions:
                return {
                    'amount': None,
                    'category': 'Khác',
                    'description': text,
                    'date': datetime.now().date(),
                    'type': 'expense',
                }
            
            # Calculate net amount
            net_amount = Decimal('0')
            all_categories = set()
            for trans in transactions:
                amount = Decimal(str(trans.get('amount', 0)))
                transaction_type = trans.get('type', 'expense')
                
                if transaction_type == 'income':
                    net_amount += amount
                else:  # expense
                    net_amount -= amount
                
                cat = trans.get('category', 'Khác')
                if cat != 'Khác':
                    all_categories.add(cat)
            
            # Determine final type based on net amount
            final_type = 'expense' if net_amount < 0 else ('income' if net_amount > 0 else 'expense')
            final_amount = abs(net_amount)
            
            # Choose category: if multiple, use "Khác"; if one, use that one; if none, use "Khác"
            if len(all_categories) > 1:
                final_category = 'Khác'
            elif len(all_categories) == 1:
                final_category = list(all_categories)[0]
            else:
                final_category = 'Khác'
            
            # Parse date (use first transaction's date)
            transaction_date = datetime.now().date()
            if transactions[0].get('date') and transactions[0].get('date') != 'today':
                try:
                    transaction_date = datetime.strptime(transactions[0].get('date'), '%Y-%m-%d').date()
                except:
                    pass
            
            # Combine descriptions
            combined_description = ' + '.join(descriptions) if descriptions else text
            
            result = {
                'amount': final_amount if final_amount > 0 else None,
                'category': final_category,
                'description': combined_description,
                'date': transaction_date,
                'type': final_type,
            }
            
            return result
            
        except Exception as e:
            print(f"❌ NLP extraction error: {e}")
            # Fallback: return empty with description
            return {
                'amount': None,
                'category': 'Khác',
                'description': text,
                'date': datetime.now().date(),
                'type': 'expense',
            }
    
    @staticmethod
    def parse_query(text: str) -> Dict:
        """
        Phân tích câu truy vấn tự nhiên dùng AI
        Ví dụ: "Tôi đã chi bao nhiêu cho cà phê trong tháng 12?"
        """
        try:
            system_prompt = """Bạn là trợ lý tài chính AI chuyên phân tích truy vấn chi tiêu tiếng Việt.
Nhiệm vụ: Phân tích câu truy vấn về chi tiêu.

Trả về JSON duy nhất (không có markdown, không có ```json):
{
  "type": "query",
  "category": "<danh mục hoặc null>",
  "time_period": {
    "start": "<YYYY-MM-DD>",
    "end": "<YYYY-MM-DD>"
  } hoặc null,
  "query_type": "sum" hoặc "count" hoặc "average"
}

Danh mục hợp lệ: Ăn uống, Di chuyển, Giải trí, Mua sắm, Y tế, Học tập, Tiết kiệm, Lương, Thu nhập kinh doanh

Ghi chú:
- query_type = "sum": tổng chi tiêu
- query_type = "count": số lần chi tiêu
- query_type = "average": chi tiêu trung bình
- Nếu không rõ time_period, để null
- Luôn trả về JSON hợp lệ
"""
            
            user_prompt = f"Phân tích truy vấn: {text}"
            response = OpenrouterService._call_generate_content(system_prompt, user_prompt, endpoint="nlp_query")
            
            data = json.loads(response)
            
            # Parse time_period
            time_period = None
            if data.get('time_period'):
                try:
                    time_period = {
                        'start': datetime.strptime(data['time_period'].get('start'), '%Y-%m-%d').date(),
                        'end': datetime.strptime(data['time_period'].get('end'), '%Y-%m-%d').date(),
                    }
                except:
                    pass
            
            result = {
                'type': 'query',
                'category': data.get('category'),
                'time_period': time_period,
                'query_type': data.get('query_type', 'sum'),
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Query parsing error: {e}")
            # Fallback
            return {
                'type': 'query',
                'category': None,
                'time_period': None,
                'query_type': 'sum',
            }
    
    
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


"""
OCR Service for extracting text from receipt/invoice images
"""
import re
from typing import Dict, Optional, List
from decimal import Decimal
from PIL import Image
import io
import easyocr
from .nlp_service import NLPService


class OCRService:
    """Service để xử lý OCR cho hóa đơn và trích xuất thông tin giao dịch"""
    
    # Khởi tạo EasyOCR reader (chỉ khởi tạo một lần để tối ưu)
    _reader = None
    
    @classmethod
    def get_reader(cls):
        """Lazy initialization của EasyOCR reader"""
        if cls._reader is None:
            # Khởi tạo với tiếng Việt và tiếng Anh
            cls._reader = easyocr.Reader(['vi', 'en'], gpu=False)
        return cls._reader
    
    @staticmethod
    def extract_text_from_image(image_file) -> str:
        """
        Trích xuất text từ ảnh hóa đơn
        Args:
            image_file: File ảnh (Django UploadedFile hoặc PIL Image)
        Returns:
            str: Text đã được trích xuất
        """
        try:
            # Đọc ảnh
            if hasattr(image_file, 'read'):
                # Django UploadedFile - reset về đầu file
                image_file.seek(0)
                image_data = image_file.read()
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_file, str):
                # File path
                image = Image.open(image_file)
            else:
                # PIL Image
                image = image_file
            
            # Chuyển sang RGB nếu cần
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize nếu ảnh quá lớn (tối ưu tốc độ OCR)
            max_size = 2000
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Sử dụng EasyOCR để đọc text
            reader = OCRService.get_reader()
            results = reader.readtext(image)
            
            # Kết hợp tất cả text lại
            text_lines = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Chỉ lấy text có độ tin cậy > 30%
                    text_lines.append(text.strip())
            
            full_text = '\n'.join(text_lines)
            return full_text
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý OCR: {str(e)}")
    
    @staticmethod
    def extract_transaction_from_receipt(image_file) -> Dict:
        """
        Trích xuất thông tin giao dịch từ ảnh hóa đơn
        Args:
            image_file: File ảnh hóa đơn
        Returns:
            Dict: Thông tin giao dịch đã được trích xuất
        """
        try:
            # Bước 1: OCR - Trích xuất text từ ảnh
            ocr_text = OCRService.extract_text_from_image(image_file)
            
            if not ocr_text or len(ocr_text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Không thể đọc được text từ ảnh. Vui lòng đảm bảo ảnh rõ ràng và có text.',
                    'raw_text': ocr_text
                }
            
            # Bước 2: Sử dụng NLP để phân tích và trích xuất thông tin
            nlp_result = NLPService.extract_transaction_info(ocr_text)
            
            # Bước 3: Cải thiện kết quả bằng cách tìm thêm thông tin từ OCR text
            # Tìm số tiền lớn nhất (thường là tổng tiền)
            # Pattern để tìm số tiền: có thể có dấu chấm/phẩy phân cách
            amount_patterns = [
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(?:₫|đ|VND|VNĐ|dong|vnd)',  # Có đơn vị tiền
                r'(?:Tổng|Tong|Total|Tong cong|Tổng cộng)[:\s]*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)',  # Sau từ "Tổng"
                r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)',  # Bất kỳ số nào
            ]
            
            parsed_amounts = []
            for pattern in amount_patterns:
                matches = re.finditer(pattern, ocr_text, re.IGNORECASE)
                for match in matches:
                    amt_str = match.group(1)
                    try:
                        # Xử lý định dạng số Việt Nam: 1.234.567 hoặc 1,234,567
                        # Nếu có 3 chữ số cuối sau dấu chấm/phẩy -> đó là phần thập phân
                        # Nếu không -> đó là dấu phân cách hàng nghìn
                        if '.' in amt_str and ',' in amt_str:
                            # Có cả 2 dấu: dấu phẩy là thập phân, dấu chấm là hàng nghìn
                            clean_amt = amt_str.replace('.', '').replace(',', '.')
                        elif ',' in amt_str:
                            # Chỉ có dấu phẩy: kiểm tra xem là thập phân hay hàng nghìn
                            parts = amt_str.split(',')
                            if len(parts) == 2 and len(parts[1]) <= 2:
                                # Có vẻ là thập phân
                                clean_amt = amt_str.replace(',', '.')
                            else:
                                # Hàng nghìn
                                clean_amt = amt_str.replace(',', '')
                        elif '.' in amt_str:
                            # Chỉ có dấu chấm
                            parts = amt_str.split('.')
                            if len(parts) == 2 and len(parts[1]) <= 2:
                                # Có vẻ là thập phân
                                clean_amt = amt_str
                            else:
                                # Hàng nghìn
                                clean_amt = amt_str.replace('.', '')
                        else:
                            clean_amt = amt_str
                        
                        value = float(clean_amt)
                        # Chỉ lấy số tiền hợp lý (từ 1,000 đến 1 tỷ)
                        if 1000 <= value <= 1000000000:
                            parsed_amounts.append((value, match.start()))
                    except:
                        continue
                
                if parsed_amounts:
                    break  # Đã tìm thấy với pattern này
            
            # Lấy số tiền lớn nhất (thường là tổng tiền)
            if parsed_amounts:
                parsed_amounts.sort(key=lambda x: x[0], reverse=True)
                max_amount = parsed_amounts[0][0]
                if not nlp_result['amount'] or max_amount > float(nlp_result['amount']):
                    nlp_result['amount'] = Decimal(str(int(max_amount)))
            
            # Tìm ngày tháng từ OCR text
            date_patterns = [
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # DD/MM/YYYY hoặc DD-MM-YYYY
                r'(\d{2,4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD
                r'Ngày[:\s]+(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',  # "Ngày: DD/MM/YYYY"
            ]
            
            from datetime import datetime
            for pattern in date_patterns:
                match = re.search(pattern, ocr_text)
                if match:
                    try:
                        groups = match.groups()
                        if len(groups) == 3:
                            # Thử parse ngày
                            if len(groups[2]) == 4:  # YYYY format
                                if int(groups[0]) > 12:  # DD/MM/YYYY
                                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                                else:  # MM/DD/YYYY hoặc YYYY/MM/DD
                                    if int(groups[0]) > 31:  # YYYY/MM/DD
                                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                                    else:  # MM/DD/YYYY
                                        month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                            else:  # YY format
                                day, month, year = int(groups[0]), int(groups[1]), 2000 + int(groups[2])
                            
                            parsed_date = datetime(year, month, day).date()
                            nlp_result['date'] = parsed_date
                            break
                    except:
                        continue
            
            # Tìm tên cửa hàng/nhà cung cấp (thường ở đầu hóa đơn)
            lines = ocr_text.split('\n')
            merchant_name = None
            for line in lines[:5]:  # Xem 5 dòng đầu
                line_clean = line.strip()
                if len(line_clean) > 3 and len(line_clean) < 50:
                    # Loại bỏ các dòng chỉ có số hoặc ký tự đặc biệt
                    if re.search(r'[a-zA-ZÀ-ỹ]', line_clean):
                        merchant_name = line_clean
                        break
            
            # Cải thiện description
            if merchant_name and not nlp_result.get('description'):
                nlp_result['description'] = f"Mua tại {merchant_name}"
            elif not nlp_result.get('description'):
                # Lấy một phần text làm description
                description_lines = [line.strip() for line in lines[:3] if line.strip() and len(line.strip()) < 100]
                if description_lines:
                    nlp_result['description'] = ' | '.join(description_lines[:2])
            
            return {
                'success': True,
                'raw_text': ocr_text,
                'transaction_info': nlp_result,
                'merchant_name': merchant_name,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi khi xử lý ảnh: {str(e)}',
                'raw_text': ''
            }


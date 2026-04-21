"""
OCR Service for extracting text from receipt/invoice images
"""
import re
import unicodedata
from typing import Dict, Optional, List
from decimal import Decimal
from PIL import Image
import io
import numpy as np
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
            
            # EasyOCR expects file path/bytes/numpy array; normalize PIL image to numpy array.
            image_np = np.array(image)

            # Sử dụng EasyOCR để đọc text
            reader = OCRService.get_reader()
            results = reader.readtext(image_np)
            
            # Gộp token theo dòng dựa trên vị trí bbox để giảm lỗi parse món.
            tokens = []
            for (bbox, text, confidence) in results:
                if confidence <= 0.2:
                    continue
                clean_text = str(text).strip()
                if not clean_text:
                    continue
                x_min = min(point[0] for point in bbox)
                x_max = max(point[0] for point in bbox)
                y_min = min(point[1] for point in bbox)
                y_max = max(point[1] for point in bbox)
                y_center = (y_min + y_max) / 2
                tokens.append((x_min, x_max, y_center, clean_text))

            if not tokens:
                return ""

            # Sort by y first, then x.
            tokens.sort(key=lambda t: (t[2], t[0]))

            line_groups = []
            y_tolerance = 12  # pixels for same text line
            for token in tokens:
                x_min, x_max, y_center, clean_text = token
                placed = False
                for group in line_groups:
                    if abs(group['y_center'] - y_center) <= y_tolerance:
                        group['tokens'].append(token)
                        group['y_center'] = (group['y_center'] + y_center) / 2
                        placed = True
                        break
                if not placed:
                    line_groups.append({'y_center': y_center, 'tokens': [token]})

            line_groups.sort(key=lambda g: g['y_center'])

            text_lines = []
            for group in line_groups:
                group_tokens = sorted(group['tokens'], key=lambda t: t[0])
                words = [t[3] for t in group_tokens]
                line = ' '.join(words).strip()
                if line:
                    text_lines.append(line)

            full_text = '\n'.join(text_lines)
            return full_text
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý OCR: {str(e)}")

    @staticmethod
    def _parse_amount_string(amount_str: str) -> Optional[Decimal]:
        """Parse amount text like 537,000 / 1.250.000 / 125000 into Decimal."""
        if not amount_str:
            return None

        s = amount_str.strip().replace(' ', '')
        # Common OCR confusion on receipts: o/O -> 0 in numeric zones.
        s = s.replace('o', '0').replace('O', '0')
        s = s.replace('l', '1').replace('I', '1')
        s = re.sub(r'[^0-9,\.]', '', s)
        if not s:
            return None

        # Both separators: assume the last separator is decimal mark, others are thousand separators.
        if ',' in s and '.' in s:
            last_comma = s.rfind(',')
            last_dot = s.rfind('.')
            if last_comma > last_dot:
                # 1.234,56 -> 1234.56
                s = s.replace('.', '')
                s = s.replace(',', '.')
            else:
                # 1,234.56 -> 1234.56
                s = s.replace(',', '')
        elif ',' in s:
            parts = s.split(',')
            # If last part has 3 digits, treat commas as thousand separators.
            if len(parts[-1]) == 3 and len(parts) > 1:
                s = ''.join(parts)
            else:
                s = s.replace(',', '.')
        elif '.' in s:
            parts = s.split('.')
            # If last part has 3 digits, treat dots as thousand separators.
            if len(parts[-1]) == 3 and len(parts) > 1:
                s = ''.join(parts)

        try:
            value = Decimal(s)
        except Exception:
            return None

        # Practical guardrails for receipt totals.
        if value < Decimal('1000') or value > Decimal('200000000'):
            return None

        return value.quantize(Decimal('1'))

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize Vietnamese text to ASCII-like lowercase for robust keyword matching."""
        if not text:
            return ''
        normalized = unicodedata.normalize('NFD', text)
        normalized = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
        normalized = normalized.replace('đ', 'd').replace('Đ', 'D')
        return normalized.lower()

    @staticmethod
    def _extract_amount_from_receipt_text(ocr_text: str) -> Optional[Decimal]:
        """Extract receipt total amount using context-aware scoring."""
        normalized_text = OCRService._normalize_text(ocr_text)

        # 1) Strong rule: prioritize number right after total/payment keywords.
        direct_total_patterns = [
            r'(?:tong\s*cong|tong\s*tien|thanh\s*toan|phai\s*tra|tien\s*mat|total|amount\s*due)\D{0,12}(\d{1,3}(?:[.,\s]\d{3})+|\d{3,9})',
        ]
        for pattern in direct_total_patterns:
            m = re.search(pattern, normalized_text, re.IGNORECASE)
            if not m:
                continue

            raw_total = m.group(1)
            parsed_total = OCRService._parse_amount_string(raw_total)

            # OCR may read "537.000" as "537" on total line -> normalize to 537000.
            if parsed_total is None:
                digits = re.sub(r'\D', '', raw_total)
                if digits.isdigit() and 3 <= len(digits) <= 4:
                    try:
                        parsed_total = Decimal(digits) * Decimal('1000')
                    except Exception:
                        parsed_total = None

            if parsed_total is not None:
                return parsed_total

        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        if not lines:
            return None

        total_keywords = re.compile(r'(tong\s*cong|tong\s*tien|thanh\s*toan|phai\s*tra|tien\s*mat|total|amount\s*due)', re.IGNORECASE)
        blocked_keywords = re.compile(r'(dt|sdt|dien\s*thoai|tel|fax|mst|ma\s*so|invoice|reg|id|bill\s*no)', re.IGNORECASE)
        amount_pattern = re.compile(r'(\d{1,3}(?:[.,\s]\d{3})+|\d{3,9})(?:\s*(?:₫|đ|vnd|vnđ))?', re.IGNORECASE)
        currency_pattern = re.compile(r'(₫|đ|vnd|vnđ)', re.IGNORECASE)

        candidates: List[tuple[Decimal, int, int]] = []
        saw_large_amount = False
        position = 0

        for line in lines:
            line_normalized = OCRService._normalize_text(line)
            has_total_keyword = bool(total_keywords.search(line_normalized))
            has_blocked_keyword = bool(blocked_keywords.search(line_normalized))
            has_currency = bool(currency_pattern.search(line_normalized))

            for m in amount_pattern.finditer(line):
                raw = m.group(1)
                value = OCRService._parse_amount_string(raw)
                if value is None:
                    # OCR hay đọc dòng tổng thành dạng rút gọn: "TIEN MAT 537"
                    # Nếu có ngữ cảnh tổng/thanhtoan thì hiểu là 537.000
                    compact = re.sub(r'\D', '', raw)
                    if has_total_keyword and compact.isdigit() and 3 <= len(compact) <= 4:
                        try:
                            value = Decimal(compact) * Decimal('1000')
                        except Exception:
                            continue
                    else:
                        continue

                score = 0
                if has_total_keyword:
                    score += 120
                if has_currency:
                    score += 40
                if ',' in raw or '.' in raw or ' ' in raw:
                    score += 20
                # Penalize phone/id-like numbers.
                if has_blocked_keyword:
                    score -= 100
                if len(re.sub(r'\D', '', raw)) >= 7 and not (',' in raw or '.' in raw or ' ' in raw) and not has_currency:
                    score -= 60

                if value >= Decimal('10000'):
                    saw_large_amount = True

                candidates.append((value, score, position))
                position += 1

        if not candidates:
            return None

        # Ưu tiên theo yêu cầu: lấy số tiền cuối cùng trong bill.
        # Loại các candidate bị nghi nhiễu mạnh và giá trị quá nhỏ.
        tail_candidates = []
        for value, score, pos in candidates:
            if score <= -80:
                continue
            if saw_large_amount and value < Decimal('10000'):
                continue
            tail_candidates.append((value, score, pos))

        if tail_candidates:
            tail_candidates.sort(key=lambda item: item[2])
            return tail_candidates[-1][0]

        # Fallback: Highest score first, then larger value.
        candidates.sort(key=lambda item: (item[1], item[0]), reverse=True)
        return candidates[0][0]

    @staticmethod
    def _extract_line_items(ocr_text: str, total_amount: Optional[Decimal] = None) -> List[Dict]:
        """Extract line items with quantity, unit_price and line_total from receipt text."""
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        if not lines:
            return []

        block_line = re.compile(
            r'(tong\s*cong|tong\s*tien|thanh\s*toan|tien\s*mat|cam\s*on|dien\s*thoai|\bdt\b|\bsdt\b|reg|invoice|mst|ma\s*so|ban\s*[:\-]|khu\s*[:\-]|phieu|thanh\s*toan|ten\s*mon|sl\s*dg|\bttien\b)',
            re.IGNORECASE,
        )
        amount_pattern = re.compile(r'(\d{1,3}(?:[.,\s]\d{3})+|\d{3,9})', re.IGNORECASE)

        items: List[Dict] = []
        seen = set()

        for raw_line in lines:
            line = re.sub(r'\s+', ' ', raw_line).strip()
            line_normalized = OCRService._normalize_text(line)
            if len(line) < 4:
                continue
            if block_line.search(line_normalized):
                continue
            if not re.search(r'[A-Za-zÀ-ỹ]', line):
                continue

            amount_matches = list(amount_pattern.finditer(line))
            if not amount_matches:
                continue

            parsed_amounts: List[tuple[Decimal, int, int]] = []
            for m in amount_matches:
                value = OCRService._parse_amount_string(m.group(1))
                if value is not None:
                    parsed_amounts.append((value, m.start(), m.end()))

            if not parsed_amounts:
                continue

            # Common formats:
            # 1) "Tên món 1 39,000 39,000" -> qty in middle, unit and total at tail
            # 2) "1 Tên món 39,000" -> qty at head, only one amount
            line_total = parsed_amounts[-1][0]
            line_total_start = parsed_amounts[-1][1]

            qty = 1
            unit_price = line_total

            if len(parsed_amounts) >= 2:
                unit_price = parsed_amounts[-2][0]

            # Prefer qty token immediately before first amount block
            first_amount_start = parsed_amounts[0][1]
            prefix_for_qty = line[:first_amount_start].strip()
            qty_match = re.search(r'(\d{1,2})\s*$', prefix_for_qty)
            if qty_match:
                try:
                    qty_val = int(qty_match.group(1))
                    if 1 <= qty_val <= 50:
                        qty = qty_val
                except Exception:
                    qty = 1

            # If no qty found, try quantity at start of line
            if qty == 1:
                start_qty_match = re.match(r'^\s*(\d{1,2})\s+', line)
                if start_qty_match:
                    try:
                        qty_val = int(start_qty_match.group(1))
                        if 1 <= qty_val <= 50:
                            qty = qty_val
                    except Exception:
                        pass

            # Derive item name: use text before the first amount block to avoid including price columns.
            name_part = line[:first_amount_start].strip(' -:|')
            name_part = re.sub(r'\b\d{1,2}\s*$', '', name_part).strip()  # qty before price columns
            name_part = re.sub(r'^\d{1,2}\s+', '', name_part).strip()     # qty at head
            name_part = re.sub(r'[^A-Za-zÀ-ỹ0-9\s\-\./]', ' ', name_part)
            name_part = re.sub(r'\s+', ' ', name_part).strip()

            if len(name_part) < 2:
                continue

            if not re.search(r'[A-Za-zÀ-ỹ]', name_part):
                continue

            # Avoid selecting total amount line if it slipped through.
            raw_line_normalized = OCRService._normalize_text(raw_line)
            if total_amount is not None and line_total == total_amount and re.search(r'(tong|total|thanh toan|tien mat)', raw_line_normalized, re.IGNORECASE):
                continue

            if re.search(r'(tong\s*cong|tong\s*tien|thanh\s*toan|tien\s*mat)', line_normalized):
                continue

            # If only one price and qty > 1, treat that amount as line total.
            if len(parsed_amounts) == 1 and qty > 1:
                try:
                    unit_price = (line_total / Decimal(qty)).quantize(Decimal('1'))
                except Exception:
                    unit_price = line_total

            item_key = (name_part.lower(), str(unit_price), str(line_total), qty)
            if item_key in seen:
                continue
            seen.add(item_key)

            items.append({
                'quantity': qty,
                'name': name_part,
                'unit_price': float(unit_price),
                'line_total': float(line_total),
            })

        # Keep at most 12 items to avoid noisy overflow.
        if items:
            return items[:12]

        # Fallback: OCR may collapse all content into one long line.
        normalized_text = re.sub(r'\s+', ' ', ocr_text).strip()
        blocked_name = re.compile(
            r'(tong\s*cong|tong\s*tien|thanh\s*toan|tien\s*mat)',
            re.IGNORECASE,
        )
        header_tokens = {
            'ten', 'mon', 'sl', 'dg', 't', 'tien', 'phieu', 'thanh', 'toan',
            'khu', 'ban', 'nv', 'so', 'tt', 'tm'
        }

        seen_fallback = set()
        fallback_items: List[Dict] = []

        tokens = normalized_text.split(' ')
        amount_indices = []
        for idx, tok in enumerate(tokens):
            val = OCRService._parse_amount_string(tok)
            if val is not None:
                amount_indices.append((idx, val))

        prev_item_end = 0
        for i in range(len(amount_indices) - 1):
            unit_idx, unit_price = amount_indices[i]
            total_idx, line_total = amount_indices[i + 1]

            # Require close numeric columns: qty unit total
            if total_idx - unit_idx > 3:
                continue

            qty_idx = unit_idx - 1
            if qty_idx < 0:
                continue

            qty_token = re.sub(r'\D', '', tokens[qty_idx])
            if not qty_token.isdigit():
                continue
            qty = int(qty_token)
            if qty < 1 or qty > 50:
                continue

            # Name is usually right before quantity in collapsed OCR output.
            # Use a local window to avoid dragging in long header text.
            window_start = max(prev_item_end, qty_idx - 4)
            name_tokens = tokens[window_start:qty_idx]
            if not name_tokens:
                name_tokens = tokens[max(0, qty_idx - 4):qty_idx]
            name = re.sub(r'\s+', ' ', ' '.join(name_tokens)).strip(' -:|')
            name = re.sub(r'[^A-Za-zÀ-ỹ0-9\s\-\./]', ' ', name)
            name = re.sub(r'\s+', ' ', name).strip()
            if len(name) < 2:
                continue

            # Trim leading table/header words that often get merged in one-line OCR output.
            parts = name.split(' ')
            while parts and OCRService._normalize_text(parts[0]) in header_tokens:
                parts.pop(0)
            name = ' '.join(parts).strip()
            if len(name) < 2:
                continue

            name_norm = OCRService._normalize_text(name)
            if blocked_name.search(name_norm):
                continue

            expected_total = (unit_price * Decimal(qty)).quantize(Decimal('1'))
            if abs(expected_total - line_total) > Decimal('2000'):
                continue

            if total_amount is not None and line_total == total_amount and 'tong cong' in name_norm:
                continue

            key = (name.lower(), qty, str(unit_price), str(line_total))
            if key in seen_fallback:
                continue
            seen_fallback.add(key)

            fallback_items.append({
                'quantity': qty,
                'name': name,
                'unit_price': float(unit_price),
                'line_total': float(line_total),
            })
            prev_item_end = total_idx + 1

        return fallback_items[:12]
    
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
            
            # Bước 3: Cải thiện kết quả bằng cách tìm số tiền theo ngữ cảnh hóa đơn
            extracted_amount = OCRService._extract_amount_from_receipt_text(ocr_text)
            if extracted_amount is not None:
                if not nlp_result['amount'] or extracted_amount != nlp_result['amount']:
                    nlp_result['amount'] = extracted_amount
            
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

            # Trích xuất danh sách món (số lượng + tên + tiền)
            items = OCRService._extract_line_items(ocr_text, nlp_result.get('amount'))

            # Cải thiện mô tả dựa trên items nếu có
            if items:
                item_parts = [f"{i['quantity']}x {i['name']}" for i in items[:3]]
                desc_from_items = '; '.join(item_parts)
                if len(items) > 3:
                    desc_from_items += f"; +{len(items) - 3} món khác"
                nlp_result['description'] = desc_from_items
            
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
                'items': items,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi khi xử lý ảnh: {str(e)}',
                'raw_text': ''
            }


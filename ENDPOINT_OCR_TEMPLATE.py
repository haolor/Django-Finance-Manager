"""
Endpoint mẫu để thêm vào views.py - OCR Receipt Template Parsing
Thêm vào class TransactionViewSet
"""

@action(detail=False, methods=['POST'])
def ocr_receipt_template(self, request):
    """Xử lý ảnh hóa đơn dùng template parsing (AI-based)"""
    if 'image' not in request.FILES:
        return Response(
            {'error': 'Vui lòng upload ảnh hóa đơn'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Kiểm tra định dạng file
    allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_formats:
        return Response(
            {'error': 'Định dạng ảnh không hỗ trợ. Vui lòng upload ảnh JPG, PNG hoặc WebP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Kiểm tra kích thước file (tối đa 10MB)
    if image_file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'Kích thước ảnh quá lớn. Vui lòng upload ảnh nhỏ hơn 10MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Bước 1: OCR - Trích xuất text từ ảnh
        ocr_text = OCRService.extract_text_from_image(image_file)
        
        if not ocr_text or len(ocr_text.strip()) < 10:
            return Response(
                {
                    'error': 'Không thể đọc được text từ ảnh. Vui lòng đảm bảo ảnh rõ ràng và có text.',
                    'raw_text': ocr_text
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Bước 2: Parse theo template (AI)
        template_result = OCRService.parse_receipt_by_template(ocr_text)
        
        if not template_result.get('success'):
            return Response(
                {
                    'error': template_result.get('error', 'Không thể parse hóa đơn theo template'),
                    'raw_text': ocr_text
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Bước 3: Tạo transaction từ kết quả
        total_amount = template_result.get('total_amount')
        if not total_amount:
            return Response(
                {
                    'error': 'Không tìm thấy số tiền trong hóa đơn',
                    'template_result': template_result
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tạo transaction
        transaction = Transaction.objects.create(
            user=request.user,
            category=None,  # Sẽ set sau
            amount=Decimal(str(total_amount)),
            description=template_result.get('address', 'Từ hóa đơn'),
            transaction_date=datetime.now().date(),
            original_nlp_input=ocr_text,
        )
        
        serializer = self.get_serializer(transaction)
        return Response(
            {
                'success': True,
                'transaction': serializer.data,
                'template_data': {
                    'customer_name': template_result.get('customer_name'),
                    'address': template_result.get('address'),
                    'items': template_result.get('items'),
                    'payment_deadline': template_result.get('payment_deadline'),
                }
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {
                'error': f'Lỗi khi xử lý ảnh: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

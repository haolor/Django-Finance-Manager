from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Category, Transaction, Budget, SpendingPattern
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    CategorySerializer, TransactionSerializer,
    BudgetSerializer, SpendingPatternSerializer
)
from .nlp_service import NLPService
from .ai_service import AIService
from .ocr_service import OCRService


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Root API endpoint"""
    return Response({
        'message': 'Finance Management System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'profile': '/api/auth/profile/',
            },
            'transactions': '/api/transactions/',
            'categories': '/api/categories/',
            'statistics': '/api/transactions/statistics/',
            'ai': {
                'trends': '/api/ai/trends/',
                'predictions': '/api/ai/predictions/',
                'anomalies': '/api/ai/anomalies/',
                'savings': '/api/ai/savings-suggestions/',
            },
            'chatbot': '/api/chatbot/',
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Đăng ký người dùng mới"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Đăng nhập"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Lấy thông tin người dùng"""
    return Response(UserSerializer(request.user).data)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet cho Category"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.all()
    
    def list(self, request):
        """Lấy danh sách categories"""
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet cho Transaction"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)
        
        # Filter theo category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter theo khoảng thời gian
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def nlp_input(self, request):
        """Xử lý nhập liệu bằng ngôn ngữ tự nhiên"""
        text = request.data.get('text', '').strip()
        if not text:
            return Response(
                {'error': 'Vui lòng nhập câu mô tả giao dịch. Ví dụ: "Hôm nay chi 50k ăn sáng"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Phân tích NLP
            nlp_result = NLPService.extract_transaction_info(text)
            
            # Kiểm tra số tiền
            if not nlp_result['amount']:
                return Response(
                    {'error': 'Không tìm thấy số tiền trong câu. Vui lòng nhập rõ số tiền.\nVí dụ: "Chi 50k ăn sáng", "Chi 100000 mua quần áo"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tìm hoặc tạo category
            category = None
            if nlp_result['category']:
                try:
                    category = NLPService.get_or_create_category(
                        nlp_result['category'],
                        nlp_result['type']
                    )
                except Exception as e:
                    # Nếu không tạo được category, vẫn tiếp tục với category = None
                    pass
            
            # Tạo transaction
            transaction = Transaction.objects.create(
                user=request.user,
                category=category,
                amount=nlp_result['amount'],
                description=nlp_result['description'],
                transaction_date=nlp_result['date'],
                original_nlp_input=text,
            )
            
            # Cập nhật spending patterns
            try:
                AIService.update_spending_patterns(request.user)
            except Exception:
                # Không block nếu update pattern thất bại
                pass
            
            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Lỗi xử lý: {str(e)}. Vui lòng thử lại với định dạng khác.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê thu chi"""
        user = request.user
        
        # Lấy khoảng thời gian
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        
        # Tính tổng thu, chi
        total_income = transactions.filter(
            category__type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        total_expense = transactions.filter(
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        balance = total_income - total_expense
        
        # Thống kê theo category
        category_stats = transactions.values(
            'category__name', 'category__type', 'category__icon', 'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Thống kê theo ngày
        daily_stats = transactions.values('transaction_date').annotate(
            income=Sum('amount', filter=Q(category__type='income')),
            expense=Sum('amount', filter=Q(category__type='expense'))
        ).order_by('transaction_date')
        
        return Response({
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            },
            'summary': {
                'total_income': float(total_income),
                'total_expense': float(total_expense),
                'balance': float(balance),
            },
            'by_category': list(category_stats),
            'by_date': [
                {
                    'date': item['transaction_date'].strftime('%Y-%m-%d'),
                    'income': float(item['income'] or 0),
                    'expense': float(item['expense'] or 0),
                }
                for item in daily_stats
            ],
        })
    
    @action(detail=False, methods=['post'])
    def ocr_receipt(self, request):
        """Xử lý ảnh hóa đơn và trích xuất thông tin giao dịch bằng OCR"""
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
            # Xử lý OCR
            ocr_result = OCRService.extract_transaction_from_receipt(image_file)
            
            if not ocr_result['success']:
                return Response(
                    {
                        'error': ocr_result.get('error', 'Không thể xử lý ảnh'),
                        'raw_text': ocr_result.get('raw_text', '')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            transaction_info = ocr_result['transaction_info']
            
            # Kiểm tra số tiền
            if not transaction_info.get('amount'):
                return Response(
                    {
                        'error': 'Không tìm thấy số tiền trong hóa đơn. Vui lòng thử lại với ảnh rõ hơn.',
                        'raw_text': ocr_result.get('raw_text', ''),
                        'extracted_info': transaction_info
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tìm hoặc tạo category
            category = None
            if transaction_info.get('category'):
                try:
                    category = NLPService.get_or_create_category(
                        transaction_info['category'],
                        transaction_info.get('type', 'expense')
                    )
                except Exception:
                    pass
            
            # Tạo transaction
            transaction = Transaction.objects.create(
                user=request.user,
                category=category,
                amount=transaction_info['amount'],
                description=transaction_info.get('description', ocr_result.get('merchant_name', 'Từ hóa đơn')),
                transaction_date=transaction_info.get('date'),
                original_nlp_input=ocr_result.get('raw_text', '')[:500],  # Lưu text OCR
            )
            
            # Cập nhật spending patterns
            try:
                AIService.update_spending_patterns(request.user)
            except Exception:
                pass
            
            serializer = self.get_serializer(transaction)
            return Response({
                'transaction': serializer.data,
                'extracted_info': {
                    'amount': float(transaction_info['amount']),
                    'category': transaction_info.get('category'),
                    'description': transaction_info.get('description'),
                    'date': transaction_info.get('date').strftime('%Y-%m-%d') if transaction_info.get('date') else None,
                    'merchant_name': ocr_result.get('merchant_name'),
                },
                'raw_text': ocr_result.get('raw_text', '')[:200],  # Preview text
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Lỗi xử lý OCR: {str(e)}. Vui lòng thử lại.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def nlp_query(self, request):
        """Truy vấn bằng ngôn ngữ tự nhiên"""
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'Query text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Phân tích query
        query_result = NLPService.parse_query(text)
        text_lower = text.lower()
        
        # Xác định loại giao dịch (income/expense) dựa trên câu hỏi
        is_expense_query = any(kw in text_lower for kw in ['chi', 'chi tiêu', 'đã chi', 'tổng chi'])
        is_income_query = any(kw in text_lower for kw in ['thu', 'thu nhập', 'tổng thu'])
        
        # Xây dựng queryset
        queryset = Transaction.objects.filter(user=request.user)
        
        # Filter theo loại giao dịch nếu có thể xác định
        if is_expense_query:
            queryset = queryset.filter(category__type='expense')
        elif is_income_query:
            queryset = queryset.filter(category__type='income')
        
        if query_result['category']:
            category = Category.objects.filter(name=query_result['category']).first()
            if category:
                queryset = queryset.filter(category=category)
        
        # Xử lý "tháng này" nếu không có time_period
        if not query_result['time_period']:
            if 'tháng này' in text_lower or 'tháng hiện tại' in text_lower:
                today = datetime.now().date()
                month_start = datetime(today.year, today.month, 1).date()
                if today.month == 12:
                    month_end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    month_end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
                queryset = queryset.filter(
                    transaction_date__gte=month_start,
                    transaction_date__lte=month_end
                )
        else:
            period = query_result['time_period']
            queryset = queryset.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        # Thực hiện query
        if query_result['query_type'] == 'sum':
            total = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            query_type_text = "chi tiêu" if is_expense_query else "thu nhập" if is_income_query else "số tiền"
            time_text = " trong tháng này" if 'tháng này' in text_lower else ""
            result = {
                'query': text,
                'result': f"Tổng {query_type_text}{time_text}: {total:,.0f}₫",
                'amount': float(total),
            }
        elif query_result['query_type'] == 'count':
            count = queryset.count()
            result = {
                'query': text,
                'result': f"Số lượng giao dịch: {count}",
                'count': count,
            }
        elif query_result['query_type'] == 'average':
            avg = queryset.aggregate(avg=Sum('amount'))['total'] or Decimal('0')
            count = queryset.count()
            if count > 0:
                avg = avg / count
            result = {
                'query': text,
                'result': f"Trung bình: {avg:,.0f} VNĐ",
                'average': float(avg),
            }
        else:
            transactions = queryset[:10]  # Limit to 10
            serializer = self.get_serializer(transactions, many=True)
            result = {
                'query': text,
                'result': f"Tìm thấy {queryset.count()} giao dịch",
                'transactions': serializer.data,
            }
        
        return Response(result)


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet cho Budget"""
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_trends(request):
    """Phân tích xu hướng chi tiêu"""
    days = int(request.query_params.get('days', 30))
    trends = AIService.analyze_spending_trends(request.user, days)
    return Response(trends)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_predictions(request):
    """Dự đoán chi tiêu tháng tiếp theo"""
    predictions = AIService.predict_next_month_spending(request.user)
    return Response(predictions)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_anomalies(request):
    """Phát hiện bất thường trong chi tiêu"""
    days = int(request.query_params.get('days', 30))
    anomalies = AIService.detect_anomalies(request.user, days)
    return Response({'anomalies': anomalies})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_savings_suggestions(request):
    """Gợi ý kế hoạch tiết kiệm"""
    suggestions = AIService.suggest_savings_plan(request.user)
    return Response(suggestions)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot(request):
    """Chatbot hỗ trợ hỏi đáp thông tin tài chính"""
    message = request.data.get('message', '')
    if not message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    message_lower = message.lower()
    
    # Xử lý các loại câu hỏi khác nhau
    if any(keyword in message_lower for keyword in ['chi bao nhiêu', 'tổng chi', 'đã chi']):
        # Truy vấn tổng chi tiêu
        query_result = NLPService.parse_query(message)
        transactions = Transaction.objects.filter(
            user=request.user,
            category__type='expense'  # Chỉ lấy chi tiêu
        )
        
        # Nếu không có time_period trong query, mặc định là tháng này
        if not query_result['time_period']:
            if 'tháng này' in message_lower or 'tháng hiện tại' in message_lower:
                today = datetime.now().date()
                month_start = datetime(today.year, today.month, 1).date()
                if today.month == 12:
                    month_end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    month_end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
                transactions = transactions.filter(
                    transaction_date__gte=month_start,
                    transaction_date__lte=month_end
                )
        else:
            period = query_result['time_period']
            transactions = transactions.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        if query_result['category']:
            category = Category.objects.filter(name=query_result['category']).first()
            if category:
                transactions = transactions.filter(category=category)
        
        total = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Thêm thông tin thời gian nếu có
        time_info = ""
        if 'tháng này' in message_lower:
            time_info = " trong tháng này"
        elif query_result['time_period']:
            time_info = f" từ {query_result['time_period']['start']} đến {query_result['time_period']['end']}"
        
        response = f"Tổng chi tiêu của bạn{time_info} là {total:,.0f}₫"
    
    elif any(keyword in message_lower for keyword in ['thu bao nhiêu', 'thu nhập', 'tổng thu']):
        # Truy vấn tổng thu nhập
        query_result = NLPService.parse_query(message)
        transactions = Transaction.objects.filter(
            user=request.user,
            category__type='income'
        )
        
        # Nếu không có time_period trong query, mặc định là tháng này
        if not query_result['time_period']:
            if 'tháng này' in message_lower or 'tháng hiện tại' in message_lower:
                today = datetime.now().date()
                month_start = datetime(today.year, today.month, 1).date()
                if today.month == 12:
                    month_end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    month_end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
                transactions = transactions.filter(
                    transaction_date__gte=month_start,
                    transaction_date__lte=month_end
                )
        else:
            period = query_result['time_period']
            transactions = transactions.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        total = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Thêm thông tin thời gian nếu có
        time_info = ""
        if 'tháng này' in message_lower:
            time_info = " trong tháng này"
        elif query_result['time_period']:
            time_info = f" từ {query_result['time_period']['start']} đến {query_result['time_period']['end']}"
        
        response = f"Tổng thu nhập của bạn{time_info} là {total:,.0f}₫"
    
    elif any(keyword in message_lower for keyword in ['số dư', 'còn lại', 'balance', 'hiện tại']):
        # Tính số dư
        transactions = Transaction.objects.filter(user=request.user)
        
        # Kiểm tra nếu hỏi về tháng này
        if 'tháng này' in message_lower or 'tháng hiện tại' in message_lower:
            today = datetime.now().date()
            month_start = datetime(today.year, today.month, 1).date()
            if today.month == 12:
                month_end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
            transactions = transactions.filter(
                transaction_date__gte=month_start,
                transaction_date__lte=month_end
            )
            time_info = " trong tháng này"
        else:
            time_info = ""
        
        total_income = transactions.filter(category__type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_expense = transactions.filter(category__type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        balance = total_income - total_expense
        
        response = f"Số dư{time_info} của bạn là {balance:,.0f}₫"
        if time_info:
            response += f"\n(Thu nhập: {total_income:,.0f}₫ - Chi tiêu: {total_expense:,.0f}₫)"
    
    elif any(keyword in message_lower for keyword in ['dự đoán', 'predict', 'tháng sau', 'chi tiêu tháng sau']):
        # Dự đoán
        predictions = AIService.predict_next_month_spending(request.user)
        confidence_text = "cao" if predictions['confidence'] == 'high' else "trung bình" if predictions['confidence'] == 'medium' else "thấp"
        response = f"📊 Dự đoán chi tiêu tháng tiếp theo: {predictions['predicted_amount']:,.0f}₫\n"
        response += f"(Độ tin cậy: {confidence_text}, dựa trên {predictions['based_on_months']} tháng gần nhất)"
    
    elif any(keyword in message_lower for keyword in ['bất thường', 'anomaly', 'lạ']):
        # Phát hiện bất thường
        anomalies = AIService.detect_anomalies(request.user)
        if anomalies:
            response = f"⚠️ Phát hiện {len(anomalies)} giao dịch bất thường:\n\n"
            
            # Hiển thị tối đa 5 giao dịch bất thường đầu tiên
            for idx, anomaly in enumerate(anomalies[:5], 1):
                icon = anomaly.get('category_icon', '💰')
                response += f"{idx}. {icon} {anomaly['amount']:,.0f}₫\n"
                response += f"   📅 Ngày: {anomaly['date']}\n"
                response += f"   📁 Danh mục: {anomaly['category']}\n"
                if anomaly.get('description') and anomaly['description'] != 'Không có mô tả':
                    response += f"   📝 Mô tả: {anomaly['description']}\n"
                if anomaly.get('deviation'):
                    # Tính phần trăm so với trung bình
                    avg = anomaly.get('avg_amount', 0)
                    if avg > 0:
                        percent_above = ((anomaly['amount'] - avg) / avg * 100)
                        response += f"   📊 Cao hơn trung bình {percent_above:.1f}% ({anomaly['deviation']:.1f} độ lệch chuẩn)\n"
                    else:
                        response += f"   📊 Độ lệch: {anomaly['deviation']:.1f} độ lệch chuẩn\n"
                response += "\n"
            
            if len(anomalies) > 5:
                response += f"... và {len(anomalies) - 5} giao dịch bất thường khác.\n"
            
            # Tính tổng số tiền bất thường
            total_anomaly = sum(a['amount'] for a in anomalies)
            response += f"\n💰 Tổng số tiền các giao dịch bất thường: {total_anomaly:,.0f}₫"
            response += f"\n\n💡 Gợi ý: Hãy xem xét lại các giao dịch này để đảm bảo tính chính xác và kiểm soát chi tiêu tốt hơn."
        else:
            response = "✅ Không phát hiện giao dịch bất thường nào. Chi tiêu của bạn đang ở mức bình thường!"
    
    elif any(keyword in message_lower for keyword in [
        'tiết kiệm', 'savings', 'gợi ý', 'cắt giảm', 'kế hoạch tiết kiệm',
        'gợi ý kế hoạch', 'cắt giảm chi tiêu', 'tiết kiệm hoặc'
    ]):
        # Gợi ý tiết kiệm
        suggestions = AIService.suggest_savings_plan(request.user)
        if suggestions['suggestions']:
            top_suggestion = suggestions['suggestions'][0]
            response = f"💰 Bạn có thể tiết kiệm {suggestions['total_potential_savings']:,.0f}₫/tháng!\n\n"
            response += f"📊 Gợi ý hàng đầu: {top_suggestion['category']}\n"
            response += f"   - {top_suggestion['suggestion']}\n"
            if top_suggestion.get('reasons'):
                response += f"   - Lý do: {', '.join(top_suggestion['reasons'][:2])}\n"
            if top_suggestion.get('actionable_tips') and len(top_suggestion['actionable_tips']) > 0:
                response += f"   - Hành động: {top_suggestion['actionable_tips'][0]}\n"
            if suggestions.get('overall_recommendation') and len(suggestions['overall_recommendation']) > 0:
                response += f"\n💡 {suggestions['overall_recommendation'][0]}"
        else:
            response = "👍 Chi tiêu của bạn đang hợp lý! Hãy tiếp tục duy trì thói quen tốt này."
    
    else:
        response = "Tôi có thể giúp bạn: hỏi về chi tiêu, thu nhập, số dư, dự đoán, phát hiện bất thường, hoặc gợi ý tiết kiệm. Bạn muốn hỏi gì?"
    
    return Response({
        'message': message,
        'response': response,
    })


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
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Phân tích NLP
        nlp_result = NLPService.extract_transaction_info(text)
        
        # Tìm hoặc tạo category
        category = None
        if nlp_result['category']:
            category = NLPService.get_or_create_category(
                nlp_result['category'],
                nlp_result['type']
            )
        
        # Tạo transaction
        if nlp_result['amount']:
            transaction = Transaction.objects.create(
                user=request.user,
                category=category,
                amount=nlp_result['amount'],
                description=nlp_result['description'],
                transaction_date=nlp_result['date'],
                original_nlp_input=text,
            )
            
            # Cập nhật spending patterns
            AIService.update_spending_patterns(request.user)
            
            serializer = self.get_serializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Could not extract amount from text'},
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
        
        # Xây dựng queryset
        queryset = Transaction.objects.filter(user=request.user)
        
        if query_result['category']:
            category = Category.objects.filter(name=query_result['category']).first()
            if category:
                queryset = queryset.filter(category=category)
        
        if query_result['time_period']:
            period = query_result['time_period']
            queryset = queryset.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        # Thực hiện query
        if query_result['query_type'] == 'sum':
            total = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            result = {
                'query': text,
                'result': f"Tổng số tiền: {total:,.0f} VNĐ",
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
    if any(keyword in message_lower for keyword in ['chi bao nhiêu', 'tổng', 'tổng cộng']):
        # Truy vấn tổng chi tiêu
        query_result = NLPService.parse_query(message)
        transactions = Transaction.objects.filter(user=request.user)
        
        if query_result['time_period']:
            period = query_result['time_period']
            transactions = transactions.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        if query_result['category']:
            category = Category.objects.filter(name=query_result['category']).first()
            if category:
                transactions = transactions.filter(category=category)
        
        total = transactions.filter(category__type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        response = f"Tổng chi tiêu của bạn là {total:,.0f} VNĐ"
    
    elif any(keyword in message_lower for keyword in ['thu bao nhiêu', 'thu nhập']):
        # Truy vấn tổng thu nhập
        query_result = NLPService.parse_query(message)
        transactions = Transaction.objects.filter(
            user=request.user,
            category__type='income'
        )
        
        if query_result['time_period']:
            period = query_result['time_period']
            transactions = transactions.filter(
                transaction_date__gte=period['start'],
                transaction_date__lte=period['end']
            )
        
        total = transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        response = f"Tổng thu nhập của bạn là {total:,.0f} VNĐ"
    
    elif any(keyword in message_lower for keyword in ['số dư', 'còn lại', 'balance']):
        # Tính số dư
        transactions = Transaction.objects.filter(user=request.user)
        total_income = transactions.filter(category__type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_expense = transactions.filter(category__type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        balance = total_income - total_expense
        response = f"Số dư hiện tại của bạn là {balance:,.0f} VNĐ"
    
    elif any(keyword in message_lower for keyword in ['dự đoán', 'predict', 'tháng sau']):
        # Dự đoán
        predictions = AIService.predict_next_month_spending(request.user)
        response = f"Dự đoán chi tiêu tháng tiếp theo: {predictions['predicted_amount']:,.0f} VNĐ"
    
    elif any(keyword in message_lower for keyword in ['bất thường', 'anomaly', 'lạ']):
        # Phát hiện bất thường
        anomalies = AIService.detect_anomalies(request.user)
        if anomalies:
            response = f"Phát hiện {len(anomalies)} giao dịch bất thường. Giao dịch lớn nhất: {anomalies[0]['amount']:,.0f} VNĐ"
        else:
            response = "Không phát hiện giao dịch bất thường nào"
    
    elif any(keyword in message_lower for keyword in ['tiết kiệm', 'savings', 'gợi ý']):
        # Gợi ý tiết kiệm
        suggestions = AIService.suggest_savings_plan(request.user)
        if suggestions['suggestions']:
            top_suggestion = suggestions['suggestions'][0]
            response = f"Bạn có thể tiết kiệm {suggestions['total_potential_savings']:,.0f} VNĐ/tháng. {top_suggestion['suggestion']}"
        else:
            response = "Chi tiêu của bạn đang hợp lý!"
    
    else:
        response = "Tôi có thể giúp bạn: hỏi về chi tiêu, thu nhập, số dư, dự đoán, phát hiện bất thường, hoặc gợi ý tiết kiệm. Bạn muốn hỏi gì?"
    
    return Response({
        'message': message,
        'response': response,
    })


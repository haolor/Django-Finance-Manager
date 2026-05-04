from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Category, Transaction, Budget, SpendingPattern, UserPreferences, Notification
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    CategorySerializer, TransactionSerializer,
    BudgetSerializer, SpendingPatternSerializer,
    UserPreferencesSerializer, NotificationSerializer
)
from .nlp_service import NLPService
from .ai_service import AIService
from .gemini_service import GeminiService
from .ocr_service import OCRService
from .notification_service import check_large_transaction, check_budget_exceeded, create_anomaly_notification


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Root API endpoint with HTTP methods for each endpoint"""
    return Response({
        'message': 'Finance Management System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': {'path': '/api/auth/register/', 'methods': ['POST']},
                'login': {'path': '/api/auth/login/', 'methods': ['POST']},
                'profile': {'path': '/api/auth/profile/', 'methods': ['GET']},
                'preferences': {'path': '/api/auth/preferences/', 'methods': ['GET','PUT','PATCH']},
            },
            'categories': {
                'list_create': {'path': '/api/categories/', 'methods': ['GET','POST']},
                'detail': {'path': '/api/categories/{id}/', 'methods': ['GET','PUT','PATCH','DELETE']},
            },
            'transactions': {
                'list_create': {'path': '/api/transactions/', 'methods': ['GET','POST']},
                'detail': {'path': '/api/transactions/{id}/', 'methods': ['GET','PUT','PATCH','DELETE']},
                'statistics': {'path': '/api/transactions/statistics/', 'methods': ['GET']},
                'expenses': {'path': '/api/transactions/expenses/', 'methods': ['GET']},
                'nlp_input': {'path': '/api/transactions/nlp_input/', 'methods': ['POST']},
                'ocr_receipt': {'path': '/api/transactions/ocr_receipt/', 'methods': ['POST']},
                'sync': {'path': '/api/transactions/sync/', 'methods': ['GET']},
                'bulk_sync': {'path': '/api/transactions/bulk_sync/', 'methods': ['POST']},
                'nlp_query': {'path': '/api/transactions/nlp_query/', 'methods': ['POST']},
            },
            'budgets': {
                'list_create': {'path': '/api/budgets/', 'methods': ['GET','POST']},
                'detail': {'path': '/api/budgets/{id}/', 'methods': ['GET','PUT','PATCH','DELETE']},
                'sync': {'path': '/api/budgets/sync/', 'methods': ['GET']},
            },
            'notifications': {
                'list_create': {'path': '/api/notifications/', 'methods': ['GET','POST']},
                'detail': {'path': '/api/notifications/{id}/', 'methods': ['GET','PUT','PATCH','DELETE']},
                'mark_read': {'path': '/api/notifications/{id}/mark_read/', 'methods': ['POST']},
                'mark_all_read': {'path': '/api/notifications/mark_all_read/', 'methods': ['POST']},
                'unread_count': {'path': '/api/notifications/unread_count/', 'methods': ['GET']},
            },
            'reports': {
                'custom': {'path': '/api/reports/custom/', 'methods': ['POST']},
            },
            'ai': {
                'trends': {'path': '/api/ai/trends/', 'methods': ['GET']},
                'predictions': {'path': '/api/ai/predictions/', 'methods': ['GET']},
                'anomalies': {'path': '/api/ai/anomalies/', 'methods': ['GET']},
                'savings': {'path': '/api/ai/savings-suggestions/', 'methods': ['GET']},
            },
            'chatbot': {'path': '/api/chatbot/', 'methods': ['POST']},
            'mobile_sync': {'path': '/api/sync/all/', 'methods': ['GET']},
        }
    })


@csrf_exempt
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


@csrf_exempt
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


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """Lấy hoặc cập nhật preferences của user"""
    try:
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = UserPreferencesSerializer(preferences)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            # Đảm bảo report_categories và dashboard_widgets là list nếu không có
            data = request.data.copy()
            if 'report_categories' not in data or data.get('report_categories') is None:
                data['report_categories'] = []
            if 'dashboard_widgets' not in data or data.get('dashboard_widgets') is None:
                data['dashboard_widgets'] = []
            
            serializer = UserPreferencesSerializer(
                preferences,
                data=data,
                partial=request.method == 'PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_custom_report(request):
    """Tạo báo cáo tùy chỉnh theo preferences"""
    from django.db.models import Sum, Count
    from collections import defaultdict
    
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)
    
    # Lấy tham số từ request hoặc dùng defaults từ preferences
    period = request.data.get('period', preferences.default_report_period)
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    categories = request.data.get('categories', preferences.report_categories)
    
    # Tính toán date range
    today = datetime.now().date()
    if period == 'week':
        start = today - timedelta(days=7)
        end = today
    elif period == 'month':
        start = datetime(today.year, today.month, 1).date()
        if today.month == 12:
            end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
    elif period == 'quarter':
        quarter = (today.month - 1) // 3 + 1
        start = datetime(today.year, (quarter - 1) * 3 + 1, 1).date()
        if quarter == 4:
            end = datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(today.year, quarter * 3 + 1, 1).date() - timedelta(days=1)
    elif period == 'year':
        start = datetime(today.year, 1, 1).date()
        end = datetime(today.year, 12, 31).date()
    else:
        start = start_date or today - timedelta(days=30)
        end = end_date or today
    
    # Query transactions
    queryset = Transaction.objects.filter(
        user=request.user,
        transaction_date__gte=start,
        transaction_date__lte=end
    )
    
    if categories:
        queryset = queryset.filter(category_id__in=categories)
    
    # Tính toán thống kê
    total_income = queryset.filter(category__type='income').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Treat uncategorized transactions as expense to keep balance consistent.
    total_expense = queryset.filter(
        Q(category__type='expense') | Q(category__isnull=True)
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    balance = total_income - total_expense
    
    # Thống kê theo category
    category_stats = queryset.values('category__name', 'category__type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Thống kê theo ngày
    daily_stats = queryset.values('transaction_date').annotate(
        income=Sum('amount', filter=Q(category__type='income')),
        expense=Sum('amount', filter=Q(category__type='expense') | Q(category__isnull=True))
    ).order_by('transaction_date')
    
    report = {
        'period': {
            'type': period,
            'start': start.isoformat(),
            'end': end.isoformat(),
        },
        'summary': {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(balance),
            'transaction_count': queryset.count(),
        },
        'category_breakdown': [
            {
                'category': item['category__name'] or 'Khác',
                'type': item['category__type'],
                'total': float(item['total']),
                'count': item['count'],
            }
            for item in category_stats
        ],
        'daily_stats': [
            {
                'date': item['transaction_date'].isoformat(),
                'income': float(item['income'] or 0),
                'expense': float(item['expense'] or 0),
            }
            for item in daily_stats
        ],
        'preferences': {
            'include_charts': preferences.report_include_charts,
            'include_tables': preferences.report_include_tables,
            'chart_type': preferences.dashboard_chart_type,
        }
    }
    
    return Response(report)


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
        transaction = serializer.save(user=self.request.user)
        
        # Kiểm tra và tạo notifications
        check_large_transaction(transaction)
        if transaction.category:
            check_budget_exceeded(self.request.user, transaction.category)
        
        # Kiểm tra anomaly và tạo notification
        try:
            # Phát hiện anomalies
            anomalies = AIService.detect_anomalies(self.request.user, days=30)
            # Kiểm tra xem transaction vừa tạo có phải là anomaly không
            for anomaly in anomalies:
                if anomaly['id'] == transaction.id:
                    # Tạo notification cho anomaly này
                    anomaly_data = {
                        'transaction': transaction,
                        'amount': transaction.amount,
                        'category': transaction.category.name if transaction.category else 'Khác',
                    }
                    create_anomaly_notification(self.request.user, anomaly_data)
                    break
        except Exception as e:
            # Không block nếu anomaly detection thất bại
            print(f"Error detecting anomaly: {e}")
        
        # Cập nhật spending patterns
        try:
            AIService.update_spending_patterns(self.request.user)
        except Exception:
            # Không block nếu update pattern thất bại
            pass
    
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
            
            # Kiểm tra và tạo notifications
            check_large_transaction(transaction)
            if transaction.category:
                check_budget_exceeded(request.user, transaction.category)
            
            # Kiểm tra anomaly và tạo notification
            try:
                # Phát hiện anomalies
                anomalies = AIService.detect_anomalies(request.user, days=30)
                # Kiểm tra xem transaction vừa tạo có phải là anomaly không
                for anomaly in anomalies:
                    if anomaly['id'] == transaction.id:
                        # Tạo notification cho anomaly này
                        anomaly_data = {
                            'transaction': transaction,
                            'amount': transaction.amount,
                            'category': transaction.category.name if transaction.category else 'Khác',
                        }
                        create_anomaly_notification(request.user, anomaly_data)
                        break
            except Exception as e:
                # Không block nếu anomaly detection thất bại
                print(f"Error detecting anomaly: {e}")
            
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
        
        period = request.query_params.get('period', None)  # e.g. 'all'
        start_date_param = request.query_params.get('start_date', None)
        end_date_param = request.query_params.get('end_date', None)

        # Nếu muốn thống kê tất cả (all-time) thì không áp dụng filter theo ngày
        if period == 'all':
            # Vẫn trả về start/end để frontend hiển thị/diagnose (không dùng cho tính toán)
            start_date = datetime(1970, 1, 1).date()
            end_date = datetime.now().date()
            transactions = Transaction.objects.filter(user=user)
        else:
            # Lấy khoảng thời gian
            if not start_date_param:
                start_date = (datetime.now() - timedelta(days=30)).date()
            else:
                try:
                    start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
                except ValueError:
                    start_date = (datetime.now() - timedelta(days=30)).date()

            if not end_date_param:
                end_date = datetime.now().date()
            else:
                try:
                    end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
                except ValueError:
                    end_date = datetime.now().date()

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
            Q(category__type='expense') | Q(category__isnull=True)
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
            expense=Sum('amount', filter=Q(category__type='expense') | Q(category__isnull=True))
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

    @action(detail=False, methods=['get'])
    def expenses(self, request):
        """
        Lấy toàn bộ giao dịch 'chi tiêu' từ DB (lọc theo category.type='expense').
        Mặc định không giới hạn theo ngày; có thể truyền start_date/end_date (YYYY-MM-DD).
        """
        queryset = self.get_queryset().select_related('category').filter(
            Q(category__type='expense') | Q(category__isnull=True)
        )

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(transaction_date__gte=start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(transaction_date__lte=end_date)
            except ValueError:
                pass

        queryset = queryset.order_by('-transaction_date', '-id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
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
            transaction_type = transaction_info.get('type', 'expense') or 'expense'
            if transaction_info.get('category'):
                try:
                    category = NLPService.get_or_create_category(
                        transaction_info['category'],
                        transaction_type
                    )
                except Exception:
                    category = None

            # Fallback category to avoid uncategorized OCR transactions.
            if category is None:
                fallback_name = 'Chi tiêu khác' if transaction_type == 'expense' else 'Thu nhập khác'
                category, _ = Category.objects.get_or_create(
                    name=fallback_name,
                    defaults={
                        'type': transaction_type,
                        'icon': '🧾',
                        'color': '#6B7280',
                        'description': 'Tự động tạo từ OCR khi không xác định được danh mục'
                    }
                )
            
            # Tạo transaction
            transaction = Transaction.objects.create(
                user=request.user,
                category=category,
                amount=transaction_info['amount'],
                description=transaction_info.get('description', ocr_result.get('merchant_name', 'Từ hóa đơn')),
                transaction_date=transaction_info.get('date'),
                original_nlp_input=ocr_result.get('raw_text', '')[:500],  # Lưu text OCR
            )
            
            # Kiểm tra và tạo notifications
            check_large_transaction(transaction)
            if transaction.category:
                check_budget_exceeded(request.user, transaction.category)
            
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
                    'items': ocr_result.get('items', []),
                },
                'raw_text': ocr_result.get('raw_text', '')[:200],  # Preview text
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Lỗi xử lý OCR: {str(e)}. Vui lòng thử lại.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Đồng bộ dữ liệu cho mobile - lấy các giao dịch đã thay đổi từ lần sync cuối
        Query params:
        - last_sync: ISO datetime string (ví dụ: 2024-01-15T10:30:00Z)
        - limit: số lượng tối đa (mặc định 100)
        """
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        last_sync_str = request.query_params.get('last_sync', None)
        limit = int(request.query_params.get('limit', 100))
        
        queryset = self.get_queryset()
        
        # Nếu có last_sync, chỉ lấy các giao dịch đã thay đổi sau thời điểm đó
        if last_sync_str:
            try:
                last_sync = parse_datetime(last_sync_str)
                if last_sync:
                    # Chuyển sang timezone aware nếu cần
                    if timezone.is_naive(last_sync):
                        last_sync = timezone.make_aware(last_sync)
                    queryset = queryset.filter(
                        Q(updated_at__gt=last_sync) | Q(created_at__gt=last_sync)
                    )
            except (ValueError, TypeError):
                pass
        
        # Sắp xếp và giới hạn
        queryset = queryset.order_by('-updated_at', '-created_at')[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Trả về thêm metadata
        return Response({
            'transactions': serializer.data,
            'count': len(serializer.data),
            'server_time': timezone.now().isoformat(),
            'has_more': len(serializer.data) == limit,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_sync(self, request):
        """
        Đồng bộ bulk cho mobile - gửi nhiều transactions cùng lúc
        Body: {
            'transactions': [
                {'id': 1, 'amount': 100000, ...},  // Update nếu có id
                {'amount': 50000, ...},  // Create nếu không có id
            ],
            'deleted_ids': [2, 3]  // IDs đã xóa trên mobile
        }
        """
        transactions_data = request.data.get('transactions', [])
        deleted_ids = request.data.get('deleted_ids', [])
        
        results = {
            'created': [],
            'updated': [],
            'deleted': [],
            'errors': []
        }
        
        # Xử lý xóa
        if deleted_ids:
            deleted_qs = Transaction.objects.filter(
                user=request.user,
                id__in=deleted_ids
            )
            deleted_count = deleted_qs.count()
            deleted_qs.delete()
            results['deleted'] = deleted_ids
            results['deleted_count'] = deleted_count
        
        # Xử lý create/update
        for idx, trans_data in enumerate(transactions_data):
            try:
                trans_id = trans_data.get('id')
                
                if trans_id:
                    # Update existing
                    try:
                        transaction = Transaction.objects.get(id=trans_id, user=request.user)
                        serializer = self.get_serializer(transaction, data=trans_data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            results['updated'].append(serializer.data)
                        else:
                            results['errors'].append({
                                'index': idx,
                                'id': trans_id,
                                'error': serializer.errors
                            })
                    except Transaction.DoesNotExist:
                        results['errors'].append({
                            'index': idx,
                            'id': trans_id,
                            'error': 'Transaction not found'
                        })
                else:
                    # Create new
                    serializer = self.get_serializer(data=trans_data)
                    if serializer.is_valid():
                        transaction = serializer.save(user=request.user)
                        results['created'].append(serializer.data)
                    else:
                        results['errors'].append({
                            'index': idx,
                            'error': serializer.errors
                        })
            except Exception as e:
                results['errors'].append({
                    'index': idx,
                    'error': str(e)
                })
        
        # Cập nhật spending patterns sau khi sync
        try:
            AIService.update_spending_patterns(request.user)
        except Exception:
            pass
        
        return Response({
            'success': True,
            'results': results,
            'summary': {
                'created_count': len(results['created']),
                'updated_count': len(results['updated']),
                'deleted_count': results.get('deleted_count', 0),
                'error_count': len(results['errors'])
            }
        }, status=status.HTTP_200_OK)
    
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


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet cho Notification"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Chỉ trả về notifications của user hiện tại"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Đánh dấu notification là đã đọc"""
        notification = self.get_object()
        if notification.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response(NotificationSerializer(notification).data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Đánh dấu tất cả notifications là đã đọc"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({'marked_read': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Lấy số lượng notifications chưa đọc"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet cho Budget"""
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def sync(self, request):
        """
        Đồng bộ budgets cho mobile
        Query params:
        - last_sync: ISO datetime string
        - limit: số lượng tối đa (mặc định 50)
        """
        from django.utils.dateparse import parse_datetime
        
        last_sync_str = request.query_params.get('last_sync', None)
        limit = int(request.query_params.get('limit', 50))
        
        queryset = self.get_queryset()
        
        if last_sync_str:
            try:
                last_sync = parse_datetime(last_sync_str)
                if last_sync:
                    if timezone.is_naive(last_sync):
                        last_sync = timezone.make_aware(last_sync)
                    queryset = queryset.filter(created_at__gt=last_sync)
            except (ValueError, TypeError):
                pass
        
        queryset = queryset.order_by('-created_at')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'budgets': serializer.data,
            'count': len(serializer.data),
            'server_time': timezone.now().isoformat(),
            'has_more': len(serializer.data) == limit,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_all(request):
    """
    Đồng bộ tất cả dữ liệu cho mobile - một endpoint duy nhất
    Query params:
    - last_sync: ISO datetime string (ví dụ: 2024-01-15T10:30:00Z)
    - transactions_limit: số lượng transactions tối đa (mặc định 100)
    - budgets_limit: số lượng budgets tối đa (mặc định 50)
    """
    from django.utils.dateparse import parse_datetime
    
    last_sync_str = request.query_params.get('last_sync', None)
    transactions_limit = int(request.query_params.get('transactions_limit', 100))
    budgets_limit = int(request.query_params.get('budgets_limit', 50))
    
    last_sync = None
    if last_sync_str:
        try:
            last_sync = parse_datetime(last_sync_str)
            if last_sync and timezone.is_naive(last_sync):
                last_sync = timezone.make_aware(last_sync)
        except (ValueError, TypeError):
            pass
    
    # Sync Transactions
    transactions_qs = Transaction.objects.filter(user=request.user)
    if last_sync:
        transactions_qs = transactions_qs.filter(
            Q(updated_at__gt=last_sync) | Q(created_at__gt=last_sync)
        )
    transactions_qs = transactions_qs.order_by('-updated_at', '-created_at')[:transactions_limit]
    transactions_serializer = TransactionSerializer(transactions_qs, many=True)
    
    # Sync Budgets
    budgets_qs = Budget.objects.filter(user=request.user)
    if last_sync:
        budgets_qs = budgets_qs.filter(created_at__gt=last_sync)
    budgets_qs = budgets_qs.order_by('-created_at')[:budgets_limit]
    budgets_serializer = BudgetSerializer(budgets_qs, many=True)
    
    # Sync Categories (tất cả vì là shared)
    categories_qs = Category.objects.all()
    categories_serializer = CategorySerializer(categories_qs, many=True)
    
    return Response({
        'transactions': {
            'data': transactions_serializer.data,
            'count': len(transactions_serializer.data),
            'has_more': len(transactions_serializer.data) == transactions_limit,
        },
        'budgets': {
            'data': budgets_serializer.data,
            'count': len(budgets_serializer.data),
            'has_more': len(budgets_serializer.data) == budgets_limit,
        },
        'categories': {
            'data': categories_serializer.data,
            'count': len(categories_serializer.data),
        },
        'server_time': timezone.now().isoformat(),
        'last_sync': last_sync.isoformat() if last_sync else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_trends(request):
    """Phân tích xu hướng chi tiêu"""
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    days = request.query_params.get('days', 30)

    start = None
    end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start = None
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end = None

    if start and end:
        trends = AIService.analyze_spending_trends(request.user, start_date=start, end_date=end)
    else:
        trends = AIService.analyze_spending_trends(request.user, int(days))
    return Response(trends)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_predictions(request):
    """Dự đoán chi tiêu tháng tiếp theo"""
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    start = None
    end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start = None
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end = None

    try:
        if start and end:
            predictions = GeminiService.predict_next_month_spending_with_ai(
                request.user, start_date=start, end_date=end
            )
        else:
            predictions = GeminiService.predict_next_month_spending_with_ai(request.user)
    except Exception as exc:
        # Fallback để API không fail nếu Gemini có sự cố
        if start and end:
            predictions = AIService.predict_next_month_spending(request.user, start_date=start, end_date=end)
        else:
            predictions = AIService.predict_next_month_spending(request.user)
        predictions['fallback_reason'] = str(exc)
        predictions['provider'] = 'local-fallback'
    return Response(predictions)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_anomalies(request):
    """Phát hiện bất thường trong chi tiêu"""
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    days = request.query_params.get('days', 30)

    start = None
    end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start = None
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end = None

    if start and end:
        anomalies = AIService.detect_anomalies(request.user, start_date=start, end_date=end)
    else:
        anomalies = AIService.detect_anomalies(request.user, int(days))
    return Response({'anomalies': anomalies})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_savings_suggestions(request):
    """Gợi ý kế hoạch tiết kiệm"""
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    start = None
    end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            start = None
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end = None

    if start and end:
        suggestions = AIService.suggest_savings_plan(request.user, start_date=start, end_date=end)
    else:
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

    try:
        ai_response = GeminiService.get_chat_response(request.user, message)
        return Response({
            'message': message,
            'response': ai_response,
            'provider': 'gemini',
            'model': getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash'),
        })
    except Exception as exc:
        # Nếu Gemini lỗi thì fallback về rule-based hiện tại
        fallback_error = str(exc)
    
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
        'provider': 'local-fallback',
        'fallback_reason': fallback_error,
    })


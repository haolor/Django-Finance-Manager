from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    api_root, register, login, user_profile,
    CategoryViewSet, TransactionViewSet, BudgetViewSet,
    ai_trends, ai_predictions, ai_anomalies, ai_savings_suggestions,
    chatbot
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/profile/', user_profile, name='user-profile'),
    path('ai/trends/', ai_trends, name='ai-trends'),
    path('ai/predictions/', ai_predictions, name='ai-predictions'),
    path('ai/anomalies/', ai_anomalies, name='ai-anomalies'),
    path('ai/savings-suggestions/', ai_savings_suggestions, name='ai-savings'),
    path('chatbot/', chatbot, name='chatbot'),
]


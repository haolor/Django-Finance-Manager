"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect, HttpResponse
from django.views.static import serve
import os

def frontend_view(request):
    """Serve frontend index.html for React Router"""
    index_path = os.path.join(settings.FRONTEND_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse('Frontend not built. Please run: cd frontend && npm run build', status=404)

def root_redirect(request):
    """Redirect root to /login"""
    return HttpResponseRedirect('/login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('finance.urls')),
    # Serve assets from frontend build
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.FRONTEND_DIR, 'assets') if os.path.exists(settings.FRONTEND_DIR) else settings.FRONTEND_DIR
    }),
    # Redirect root to login
    path('', root_redirect, name='root'),
    # Serve frontend for all other routes (React Router)
    re_path(r'^(?!admin|api|static|assets).*$', frontend_view, name='frontend'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

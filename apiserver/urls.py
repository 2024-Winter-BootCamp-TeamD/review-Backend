"""
URL configuration for apiserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Review API",
        default_version='v1',
        description="Review API",
        terms_of_service="",
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pullrequest.urls')),  # 풀리퀘스트 엔드포인트
    path('api/', include('user.urls')),  # 사용자 엔드포인트
    path('api/v1/', include('oauth.urls')),
    path('', include('review.urls')),
    path('api/', include('partreview.urls')), # 드래그 코드 엔드포인트
    path('api/', include('report.urls')), # 보고서 엔드포인트
    path('api/v1/', include('repository.urls')),  # 레포지토리 엔드포인트
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger')
]


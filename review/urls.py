from django.urls import path
from . import views

urlpatterns = [

    #GitHub에서 웹훅 이벤트를 수신하는 엔드포인트
    path('github/webhook/', views.github_webhook, name='github_webhook'),
]
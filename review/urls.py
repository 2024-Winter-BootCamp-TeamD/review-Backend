from django.urls import path
from review.views import github_webhook

urlpatterns = [

    #GitHub에서 웹훅 이벤트를 수신하는 엔드포인트
    path('github/webhook/', github_webhook, name='github_webhook'),
]
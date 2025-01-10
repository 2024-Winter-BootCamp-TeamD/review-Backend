from django.urls import path
from . import views

urlpatterns = [
    path('oauth/login/',  views.LoginGithubView.as_view(), name='login_auth_github'), # 깃허브 연동
    path('login/github/callback/', views.LoginGithubCallbackView.as_view(), name='login_github_callback'), # 연동 후 콜백

    # 리포지토리에 웹훅 설정
    path('github/orgs/<str:org_name>/repos/<str:repo_name>/setup-webhook/', views.setup_webhook.as_view(), name='setup_webhook'),

    # GitHub에서 웹훅 이벤트를 수신하는 엔드포인트
    path('github/webhook/', views.github_webhook.as_view(), name='github_webhook'),
]
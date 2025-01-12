from django.urls import path
from . import views

urlpatterns = [
    path('oauth/login/',  views.LoginGithubView.as_view(), name='login_auth_github'), # 깃허브 연동
    path('oauth/login/github/callback/', views.LoginGithubCallbackView.as_view(), name='login_github_callback'), # 연동 후 콜백
]
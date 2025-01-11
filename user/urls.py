from django.urls import path
from .views import UserDetailView
from .views import UserModeUpdateView

urlpatterns = [
    path('v1/users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('v1/users/<int:user_id>/mode/' , UserModeUpdateView.as_view(), name='user-mode-update')
]

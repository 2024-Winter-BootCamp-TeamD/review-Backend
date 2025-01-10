from django.urls import path
from .views import UserDetailView

urlpatterns = [
    path('v1/users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
]

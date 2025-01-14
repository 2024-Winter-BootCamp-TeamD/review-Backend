from django.urls import path
from . import views
from .views import get_repositories

urlpatterns = [
    path('repositories/', get_repositories, name='get_repositories'),
]
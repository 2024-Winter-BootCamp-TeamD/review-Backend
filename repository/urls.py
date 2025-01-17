from django.urls import path
from . import views
from .views import get_repositories
from .views import ApplyRepositoryView
urlpatterns = [
    path('repositories/', get_repositories, name='get_repositories'),
    path('repositories/select/', ApplyRepositoryView.as_view(), name='ApplyRepositoryView'),
]


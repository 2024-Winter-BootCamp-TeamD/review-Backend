from django.urls import path
from . import views
from .views import get_repositories, get_acitve, get_inacitve, get_search

from .views import ApplyRepositoryView
urlpatterns = [
    path('repositories/', get_repositories, name='get_repositories'),
    path('repositories/select/', ApplyRepositoryView.as_view(), name='ApplyRepositoryView'),

    path('repositories/active/',get_acitve, name='get_acitve'),

    path('repositories/inactive/',get_inacitve, name='get_inactive'),

    path('repositories/search/',get_search, name='get_search'),
]

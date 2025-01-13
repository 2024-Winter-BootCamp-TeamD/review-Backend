from django.urls import path
from .views import PRReviewListView, PRReviewSearchView

urlpatterns = [
    path('v1/pr-reviews/', PRReviewListView.as_view(), name='pr-review-list'),
    path('v1/pr-reviews/search', PRReviewSearchView.as_view(), name='pr-review-search'),
]

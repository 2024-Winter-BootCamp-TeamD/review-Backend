from django.urls import path
from .views import PRReviewListView

urlpatterns = [
    path('api/v1/pr-reviews', PRReviewListView.as_view(), name='pr-review-list'),
]

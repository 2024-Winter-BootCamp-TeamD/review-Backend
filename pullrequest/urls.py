from django.urls import path
from .views import PRReviewListView, PRReviewSearchView, PRReviewAverageGradeView

urlpatterns = [
    path('v1/pr-reviews/', PRReviewListView.as_view(), name='pr-review-list'),
    path('v1/pr-reviews/search', PRReviewSearchView.as_view(), name='pr-review-search'),
    path('v1/pr-reviews/aver-grade', PRReviewAverageGradeView.as_view(), name='pr-review-aver-grade'),
]


from django.urls import path
from .views import PRReviewListView, PRReviewSearchView, PRReviewTroubleTypeView, \
    PRReviewCategoryStatisticsView, PRReviewRecentAverageGradeView, PRReviewAllAverageGradeView, PRReviewSelectView

urlpatterns = [
    path('v1/pr-reviews/', PRReviewListView.as_view(), name='pr-review-list'),
    path('v1/pr-reviews/aver-grade/all', PRReviewAllAverageGradeView.as_view(), name='pr-review-aver-grade-all'),
    path('v1/pr-reviews/trouble-type', PRReviewTroubleTypeView.as_view(), name='pr-review-trouble-type'),
    path('v1/pr-reviews/category', PRReviewCategoryStatisticsView().as_view(), name='pr-review-category'),
    path('v1/pr-reviews/select', PRReviewSelectView.as_view(), name='pr-review-select'),
]


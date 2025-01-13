from django.urls import path
from .views import PartReviewView

urlpatterns = [
    path('v1/partreviews/', PartReviewView.as_view(), name='part-review-request'),
]

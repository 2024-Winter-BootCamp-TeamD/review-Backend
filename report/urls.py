from django.urls import path
from .views import ReportAPIView, ReportDetailAPIView, ReportDownloadAPIView

urlpatterns = [
    path('v1/reports/', ReportAPIView.as_view(), name='report-list-create'),
    path('v1/reports/<int:report_id>/', ReportDetailAPIView.as_view(), name='report-detail'),
    path('v1/reports/<int:report_id>/download/', ReportDownloadAPIView.as_view(), name='report-download'),
]

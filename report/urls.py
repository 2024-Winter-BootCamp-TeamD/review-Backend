from django.urls import path
from .views import UserReportAPIView, ReportDetailAPIView, ReportDeleteAPIView, ReportDownloadAPIView, ReportModeAPIView

urlpatterns = [
    path('v1/reports/<int:user_id>/', UserReportAPIView.as_view(), name='user-reports'),  # GET & POST
    path('v1/reports/<int:report_id>/detail/', ReportDetailAPIView.as_view(), name='report-detail'),  # GET
    path('v1/reports/<int:report_id>/delete/', ReportDeleteAPIView.as_view(), name='report-delete'),  # DELETE
    path('v1/reports/<int:report_id>/download/', ReportDownloadAPIView.as_view(), name='report-download'),  # GET
    path('v1/reports/<int:report_id>/mode/', ReportModeAPIView.as_view(), name='report-modes'),  # GET
]
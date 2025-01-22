from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from report.models import Report, ReportPrReview
from user.models import User
from pullrequest.models import PRReview
from django.utils.timezone import now
from io import BytesIO
from report.views import UserReportAPIView


class ReportAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            github_id="12345",
            github_username="test_user",
            email="test@example.com"
        )
        self.report = Report.objects.create(
            user=self.user,
            title="Test Report",
            content="This is a test report.",
            review_num=1,
            pdf_url="/path/to/pdf"
        )
        self.pr_review = PRReview.objects.create(
            title="Test PR",
            problem_type="명명규칙",
            review_mode="clean",
            total_review=5,
            user=self.user
        )

    def test_create_report(self):
        # Given
        url = reverse("user-reports", kwargs={"user_id": self.user.id})

        # 필요한 PRReview 데이터 생성
        pr_ids = [20, 6, 26, 27, 12]
        for pr_id in pr_ids:
            PRReview.objects.create(
                id=pr_id,
                title=f"PR {pr_id}",
                problem_type="명명규칙",
                review_mode="clean",
                total_review=5,
                user=self.user
            )

        data = {
            "report_title": "테스트 보고서",
            "pr_ids": pr_ids
        }

        # When
        response = self.client.post(url, data, content_type="application/json")
        print(response.json())

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertIn("report_id", response.json())

    def test_delete_report(self):
        # Given
        url = reverse("report-delete", kwargs={"report_id": self.report.report_id})

        # When
        response = self.client.delete(url)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertTrue(self.report.is_deleted)

    def test_reportprreview_creation(self):
        # Given
        # When
        report_pr_review = ReportPrReview.objects.create(
            report=self.report,
            pr_review=self.pr_review
        )

        # Then
        self.assertEqual(report_pr_review.report.title, "Test Report")
        self.assertEqual(report_pr_review.pr_review.title, "Test PR")


class ReportUtilityTest(TestCase):
    def test_generate_pdf(self):
        # Given
        report_data = {
            "title": "Sample Report",
            "author": "Test User",
            "created_date": now().strftime("%Y-%m-%d"),
            "review_table": [
                {"id": 1, "title": "PR 1", "aver_grade": 4.5, "created_at": "2025-01-01"},
                {"id": 2, "title": "PR 2", "aver_grade": 3.8, "created_at": "2025-01-02"},
            ],
            "analysis": "This is a sample analysis text.",
        }

        # When
        pdf_buffer = UserReportAPIView().generate_styled_pdf("Test Report", report_data)

        # Then
        self.assertIsInstance(pdf_buffer, BytesIO)
        self.assertGreater(len(pdf_buffer.getvalue()), 0)

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import PRReview
from user.models import User


class PRReviewAPITest(TestCase):
    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create(
            github_id="12345",
            github_username="test_user",
            email="test@example.com"
        )
        # PR 리뷰 데이터 생성
        for i in range(1, 12):  # 11개의 PR 리뷰 생성
            PRReview.objects.create(
                user=self.user,
                title=f"PR {i}",
                pr_url=f"http://example.com/pr/{i}",
                aver_grade="A" if i % 2 == 0 else "B",
                problem_type="Convention" if i % 2 == 0 else "Algorithm",
                review_mode="clean" if i % 2 == 0 else "optimize",
                total_review=f"Review content {i}"
            )
        self.client = APIClient()

    def print_response(self, step, response):
        print(f"Response Data {step}: {response.status_code}, {response.data}")

    def test_pr_review_list_view(self):
        # Given
        url = reverse("pr-review-list") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(1, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_pr_review_search_view(self):
        # Given
        url = reverse("pr-review-search") + f"?user_id={self.user.id}&title=PR 1"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(2, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_pr_review_recent_average_grade_view(self):
        # Given
        url = reverse("pr-review-aver-grade-recent") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(3, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_pr_review_all_average_grade_view(self):
        # Given
        url = reverse("pr-review-aver-grade-all") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(4, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_pr_review_trouble_type_view(self):
        # Given
        url = reverse("pr-review-trouble-type") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(5, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_pr_review_category_statistics_view(self):
        # Given
        url = reverse("pr-review-category") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Then
        self.print_response(6, response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("statistics", response.data)

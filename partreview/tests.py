from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from user.models import User
import json


class PartReviewAPITest(TestCase):
    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create(
            github_id="12345",
            github_username="test",
            email="test@example.com",
            review_mode="clean"
        )
        self.client = APIClient()

    def collect_streaming_content(self, response):
        """스트리밍 응답 데이터를 모두 수집하여 하나의 문자열로 반환."""
        content = ''.join(chunk.decode('utf-8') for chunk in response.streaming_content)
        return content

    def test_part_review_request_success(self):
        # Given
        url = reverse("part-review-request")
        data = {
            "userId": self.user.id,
            "code": "def test_function():\n    return True"
        }

        # When
        response = self.client.post(url, json.dumps(data), content_type="application/json", stream=True)

        # Then
        combined_content = self.collect_streaming_content(response)
        print(f"Combined Response Data 1:\n{combined_content}")
        self.assertEqual(response.status_code, 200)

    def test_part_review_request_missing_data(self):
        # Given
        url = reverse("part-review-request")
        data = {
            "userId": self.user.id
            # "code"가 빠진 데이터
        }

        # When
        response = self.client.post(url, json.dumps(data), content_type="application/json", stream=True)

        # Then
        combined_content = self.collect_streaming_content(response)
        print(f"Combined Response Data 2:\n{combined_content}")
        self.assertEqual(response.status_code, 200)

    def test_part_review_request_invalid_user(self):
        # Given
        url = reverse("part-review-request")
        data = {
            "userId": 9999,  # 존재하지 않는 userId
            "code": "def invalid_user_test():\n    pass"
        }

        # When
        response = self.client.post(url, json.dumps(data), content_type="application/json", stream=True)

        # Then
        combined_content = self.collect_streaming_content(response)
        print(f"Combined Response Data 3:\n{combined_content}")
        self.assertEqual(response.status_code, 200)

    def test_part_review_request_api_error(self):
        # Given
        url = reverse("part-review-request")
        data = {
            "userId": self.user.id,
            "code": "raise_error_test()"
        }

        # Mocking API 호출 에러를 유발
        with self.settings(DEEPSEEK_API_URL="https://invalid.url"):
            response = self.client.post(url, json.dumps(data), content_type="application/json", stream=True)

        # Then
        combined_content = self.collect_streaming_content(response)
        print(f"Combined Response Data 4:\n{combined_content}")
        self.assertEqual(response.status_code, 200)

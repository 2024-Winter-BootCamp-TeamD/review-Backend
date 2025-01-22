from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User
import json

class UserAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            github_id="12345",
            github_username="test_user",
            email="test@example.com",
            review_mode="clean"
        )
        self.client = APIClient()

    def test_user_detail_view_success(self):
        # Given
        url = reverse("user-detail", kwargs={"user_id": self.user.id})

        # When
        response = self.client.get(url)
        print("Response Data1:", response.data)
        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["github_id"], "12345")
        self.assertEqual(response.data["github_username"], "test_user")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_user_detail_view_not_found(self):
        # Given
        url = reverse("user-detail", kwargs={"user_id": 9999})  # 존재하지 않는 ID

        # When
        response = self.client.get(url)
        print("Response Data2:", response.data)
        # Then
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")

    def test_user_mode_update_success(self):
        # Given
        url = reverse("user-mode-update", kwargs={"user_id": self.user.id})
        data = {"review_mode": "clean"}

        # When
        response = self.client.put(url, json.dumps(data), content_type="application/json")
        print("Response Data3:", response.data)
        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_mode"], "clean")

    def test_user_mode_update_invalid_mode(self):
        # Given
        url = reverse("user-mode-update", kwargs={"user_id": self.user.id})
        data = {"review_mode": "invalid_mode"}  # 유효하지 않은 모드

        # When
        response = self.client.put(url, json.dumps(data), content_type="application/json")
        print("Response Data4:", response.data)
        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("\"invalid_mode\" is not a valid choice", str(response.data))

    def test_user_mode_update_not_found(self):
        # Given
        url = reverse("user-mode-update", kwargs={"user_id": 9999})  # 존재하지 않는 ID
        data = {"review_mode": "optimize"}

        # When
        response = self.client.put(url, json.dumps(data), content_type="application/json")
        print("Response Data5:", response.data)
        # Then
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Repository, User
from django.utils.timezone import now
import json


class RepositoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            github_id="12345",
            github_username="test_user",
            email="test@example.com",
        )

        self.repo1 = Repository.objects.create(
            user_id=self.user,
            repository_github_id="repo1",
            name="Test Repo 1",
            organization="Test Org",
            is_apply=True,
            visibility="public",
            repo_updated_at=now(),
        )

        self.repo2 = Repository.objects.create(
            user_id=self.user,
            repository_github_id="repo2",
            name="Test Repo 2",
            organization="Test Org",
            is_apply=False,
            visibility="private",
            repo_updated_at=now(),
        )

    def test_get_repositories_success(self):
        # Given
        url = reverse("get_repositories") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Debug: Print response
        print("Response Data1:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("repositories", response.data)
        self.assertEqual(len(response.data["repositories"]), 2)

    def test_get_repositories_missing_user_id(self):
        # Given
        url = reverse("get_repositories")

        # When
        response = self.client.get(url)

        # Debug: Print response
        print("Response Data2:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_active_repositories(self):
        # Given
        url = reverse("get_acitve") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Debug: Print response
        print("Response Data3:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["repositories"]), 1)
        self.assertEqual(response.data["repositories"][0]["name"], "Test Repo 1")

    def test_get_inactive_repositories(self):
        # Given
        url = reverse("get_inactive") + f"?user_id={self.user.id}"

        # When
        response = self.client.get(url)

        # Debug: Print response
        print("Response Data4:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["repositories"]), 1)
        self.assertEqual(response.data["repositories"][0]["name"], "Test Repo 2")

    def test_search_repositories(self):
        # Given
        url = reverse("get_search") + f"?user_id={self.user.id}&search_query=Test Repo 1"

        # When
        response = self.client.get(url)

        # Debug: Print response
        print("Response Data5:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["repositories"]), 1)
        self.assertEqual(response.data["repositories"][0]["name"], "Test Repo 1")

    def test_apply_repository_success(self):
        # Given
        url = reverse("ApplyRepositoryView")
        data = {
            "repositories": [self.repo2.id],  # 올바른 repo ID 사용
            "is_apply": True,  # Boolean 값 사용
        }

        # When
        response = self.client.post(url, json.dumps(data), content_type="application/json")  # JSON 직렬화

        # Debug: Response 출력
        print("Response Data6:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.repo2.refresh_from_db()
        self.assertTrue(self.repo2.is_apply)

    def test_apply_repository_invalid_data(self):
        # Given
        url = reverse("ApplyRepositoryView")
        data = {
            "repositories": [self.repo2.id],  # 올바른 repo ID 사용
            "is_apply": "invalid_value",  # Boolean이 아닌 잘못된 값
        }

        # When
        response = self.client.post(url, json.dumps(data), content_type="application/json")  # JSON 직렬화

        # Debug: Response 출력
        print("Response Data7:", response.data)

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_apply는 boolean이어야 합니다.", str(response.data))

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from user.models import User
from repository.models import Repository
import json


class OAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 테스트 유저 생성
        self.user = User.objects.create(
            github_id="12345",
            github_username="test_user",
            email="test@example.com",
            review_mode="clean"
        )

    @patch("requests.post")
    @patch("requests.get")
    def test_login_github_callback_success(self, mock_get, mock_post):
        # Mocking GitHub OAuth2 토큰 응답
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "mock_access_token"}
        )

        # Mocking GitHub 사용자 정보 및 레포지토리 정보 응답
        mock_get.side_effect = [
            MagicMock(  # 사용자 정보 응답
                status_code=200,
                json=lambda: {
                    "id": 12345,
                    "login": "test_user",
                    "email": "test@example.com",
                    "avatar_url": "https://example.com/avatar.png",
                }
            ),
            MagicMock(  # 개인 레포지토리 정보 응답
                status_code=200,
                json=lambda: [
                    {
                        "id": 1,
                        "name": "test_repo",
                        "owner": {"login": "test_user", "avatar_url": "https://example.com/avatar.png"},
                        "language": "Python",
                        "description": "Test repository",
                        "visibility": "public",
                        "updated_at": "2025-01-01T00:00:00Z",
                    }
                ]
            ),
            MagicMock(  # 조직 정보 응답
                status_code=200,
                json=lambda: [
                    {"login": "test_org"}
                ]
            ),
            MagicMock(  # 조직 레포지토리 정보 응답
                status_code=200,
                json=lambda: [
                    {
                        "id": 2,
                        "name": "org_repo",
                        "owner": {"login": "test_org", "avatar_url": "https://example.com/org_avatar.png"},
                        "language": "JavaScript",
                        "description": "Organization repository",
                        "visibility": "private",
                        "updated_at": "2025-01-02T00:00:00Z",
                    }
                ]
            )
        ]

        # Callback URL 요청
        callback_url = reverse("login_github_callback")
        response = self.client.get(callback_url, {"code": "mock_code"})

        # 응답 데이터 확인 및 출력
        response_content = response.content.decode('utf-8')  # JSON 문자열로 디코딩
        print("Response Data1:", response_content)

        # JSON 파싱 후 검증
        response_data = json.loads(response_content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response_data)
        self.assertIn("user", response_data)

        # Repository 모델에 저장된 데이터 확인
        repositories = Repository.objects.all()
        self.assertEqual(len(repositories), 2)

        # 개인 레포지토리 검증
        personal_repo = repositories.get(name="test_repo")
        self.assertEqual(personal_repo.language, "Python")
        self.assertEqual(personal_repo.organization, "test_user")

        # 조직 레포지토리 검증
        org_repo = repositories.get(name="org_repo")
        self.assertEqual(org_repo.language, "JavaScript")
        self.assertEqual(org_repo.organization, "test_org")

    def test_login_github_redirect(self):
        # Redirect URL 요청
        login_url = reverse("login_auth_github")
        response = self.client.get(login_url)

        # Redirect URL 확인 및 출력
        print("Response Data2:", response.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://github.com/login/oauth/authorize", response.url)

    @patch("requests.post")
    def test_login_github_callback_failure(self, mock_post):
        # Mocking GitHub OAuth2 토큰 실패 응답
        mock_post.return_value = MagicMock(
            status_code=400,
            json=lambda: {"error": "invalid_grant"}
        )

        # Callback URL 요청
        callback_url = reverse("login_github_callback")
        response = self.client.get(callback_url, {"code": "mock_code"})

        # 응답 데이터 확인 및 출력
        response_content = response.content.decode('utf-8')  # JSON 문자열로 디코딩
        print("Response Data3:", response_content)

        # JSON 파싱 후 검증
        response_data = json.loads(response_content)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response_data)

    @patch("requests.post")
    def test_login_github_callback_missing_code(self, mock_post):
        # Callback URL 요청 (code가 없음)
        callback_url = reverse("login_github_callback")
        response = self.client.get(callback_url)

        # 응답 데이터 확인 및 출력
        response_content = response.content.decode('utf-8')  # JSON 문자열로 디코딩
        print("Response Data4:", response_content)

        # JSON 파싱 후 검증
        response_data = json.loads(response_content)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response_data)

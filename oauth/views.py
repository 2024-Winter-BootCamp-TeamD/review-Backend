from django.http import JsonResponse

# Create your views here.
import os

import requests
from django.shortcuts import redirect
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from repository.models import Repository
from oauth.utils.loginUtils import social_user_get_or_create
from user.models import User

# Create your views here.
load_dotenv()


class LoginGithubView(APIView):
    def get(self, request):
        # 깃허브 oauth2 로그인 페이지로 리다이렉트
        github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={os.getenv("GITHUB_REDIRECT_URI")}&scope=repo,read:org,public_repo,write:discussion"
        return redirect(github_oauth_url)


# 나중에 리팩토링으로 함수로 나눠야 함
class LoginGithubCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        # GitHub 액세스 토큰 요청
        token_url = "https://github.com/login/oauth/access_token"
        payload = {
            'client_id': os.getenv("GITHUB_CLIENT_ID"),
            'client_secret': os.getenv("GITHUB_CLIENT_SECRET"),
            'code': code,
            'redirect_uri': os.getenv("GITHUB_REDIRECT_URI")
        }
        response = requests.post(token_url, data=payload, headers={'Accept': 'application/json'})
        response_data = response.json()

        if 'access_token' not in response_data:
            return Response({"error": "깃허브 액세스 토큰을 받는데 실패 하였습니다."}, status=status.HTTP_400_BAD_REQUEST)

        access_token = response_data.get('access_token')

        # 사용자의 GitHub 사용자명 정보 가져오기
        user_info_url = "https://api.github.com/user"
        headers = {'Authorization': f'token {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_data = user_info_response.json()
        print(user_data)
        user_profile, created = social_user_get_or_create(
            github_id=user_data["id"],
            github_username=user_data["login"],
            email=user_data["email"],
            profile_image=user_data["avatar_url"],
            access_token=access_token
        )

        # 메시지 설정
        if created:
            message = "회원가입에 성공하였습니다."
        else:
            message = "로그인에 성공하였습니다."

        ### 레포지토리 긁어와 전부 우선 DB에 저장, 이때 기능 적용 여부는 default로 False로 적용
        repos = []

        # 개인레포 읽어오기
        self.GetPersonalRepos(access_token, repos, user_data)

        # 오가니제이션 읽어오기
        self.GetOrgsRepos(access_token, repos)

        # 모든 레포를 가져온 repo를 각각 db에 저장
        user = User.objects.get(id=user_profile.id)
        for repo in repos:
            # repository_github_id로 이미 존재하는지 확인
            if Repository.objects.filter(repository_github_id=repo['id']).exists():
                print(f"Repository with ID {repo['id']} already exists. Skipping...")
                continue  # 이미 존재하면 건너뛰기

            repository = Repository(
                user_id=user,
                repository_github_id=repo['id'],
                is_apply=False,
                organization=repo['owner']['login'],
                name=repo['name'],
                repository_image=repo['owner']['avatar_url']
            )
            repository.full_clean()
            repository.save()

        # JSON 응답
        response_data = {
            "message": message,
            "user": {
                "id": user_profile.id,
                "github_username": user_profile.github_username,
                "email": user_profile.email,
                "profile_image": user_profile.profile_image,
            },
        }

        return JsonResponse(response_data, status=200)

    def GetOrgsRepos(self, access_token, repos):
        headers = {
            'Authorization': f'token {access_token}'
        }
        response = requests.get('https://api.github.com/user/orgs', headers=headers)
        orgs = response.json()
        for org in orgs:
            headers = {
                'Authorization': f'token {access_token}'
            }
            response = requests.get(f'https://api.github.com/orgs/{org["login"]}/repos', headers=headers)
            repos.extend(response.json())

    def GetPersonalRepos(self, access_token, repos, user_data):
        headers = {
            'Authorization': f'token {access_token}'
        }
        response = requests.get(f'https://api.github.com/users/{user_data["login"]}/repos', headers=headers)
        repos.extend(response.json())

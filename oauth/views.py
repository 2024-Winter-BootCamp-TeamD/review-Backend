from django.shortcuts import render

# Create your views here.
import os

import requests
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apiserver import settings


# Create your views here.
load_dotenv()

class LoginGithubView(APIView):
    def get(self, request):
        # 깃허브 oauth2 로그인 페이지로 리다이렉트
        github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={os.getenv("GITHUB_REDIRECT_URI")}&scope=repo,read:org,public_repo,write:discussion"
        return redirect(github_oauth_url)

class LoginGithubCallbackView:
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({"error": "잘못된 깃허브 인가코드 입니다."}, status=status.HTTP_400_BAD_REQUEST)

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
        user_info = user_info_response.json()



        return Response({"user_info": user_info}, status=status.HTTP_200_OK)

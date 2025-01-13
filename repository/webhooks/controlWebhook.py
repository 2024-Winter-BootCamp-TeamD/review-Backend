import os

import requests
from django.http import JsonResponse
from dotenv import load_dotenv

from repository.models import Repository

load_dotenv()

# 레포지토리에 웹훅을 거는 함수
def createWebhook(organization, repo_name, access_token, repository_id):
    repo_path = f"{organization}/{repo_name}"

    existing_webhook = Repository.objects.filter(repository_id=repository_id, is_apply=True).exists()
    if existing_webhook:
        return {"status": "error", "message": f"Webhook already exists for {repo_path}"}

    url = f'https://api.github.com/repos/{repo_path}/hooks'
    print(f"Repository Path: {repo_path}")
    print(f"Requesting URL: {url}")
    headers = {
        'Authorization': f'token {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "name": "web",
        "active": True,
        "events": ["pull_request"],  # PR 관련 이벤트만 받음
        "config": {
            "url": f"{os.getenv("GITHUB_WEBHOOK_URL")}",  # 로컬 웹훅 수신 URL
            "content_type": "json"
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 4xx, 5xx 오류 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Create Webhook Request failed: {str(e)}"}
    # 응답 처리
    if response.status_code == 201:
        webhook_data = response.json()
        repository = Repository.objects.get(id=repository_id)
        repository.hook_id = webhook_data['id']
        repository.is_apply = True
        repository.save()
        return {"status": "success", "message": f"Webhook created successfully for {repo_path}", "data": webhook_data}
    else:
        return {"status": "error", "message": f"Failed to create webhook for {repo_path}: {response.status_code} - {response.text}"}


# 웹훅을 활성화 시키는 함수
def activateWebhook(organization, repo_name, access_token, hook_id, repository_id):
    repo_path = f"{organization}/{repo_name}"
    url = f'https://api.github.com/repos/{repo_path}/hooks/{hook_id}'
    headers = {
        'Authorization': f'token {access_token}',
        'Content-Type': 'application/json'
    }
    # 활성화 데이터
    data = {
        "active": True
    }
    # PATCH 요청 보내기
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()  # 4xx, 5xx 오류 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"active Webhook(id:{hook_id}) Request failed: {str(e)}"}
    # 응답 처리
    if response.status_code == 200:
        repository = Repository.objects.get(id=repository_id)
        repository.is_apply = True
        repository.save()
        return {"status": "success", "message": f"Webhook(id:{hook_id}) activated successfully."}
    else:
        return {"status": "error",
                "message": f"Failed to activate webhook(id:{hook_id}): {response.status_code} - {response.text}"}


# 웹훅을 비활성화 시키는 함수
def deactivateWebhook(organization, repo_name, access_token, hook_id, repository_id):
    repo_path = f"{organization}/{repo_name}"
    url = f'https://api.github.com/repos/{repo_path}/hooks/{hook_id}'
    headers = {
        'Authorization': f'token {access_token}',
        'Content-Type': 'application/json'
    }
    # 비활성화 데이터
    data = {
        "active": False
    }
    # PATCH 요청 보내기
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()  # 4xx, 5xx 오류 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"deactive Webhook(id:{hook_id}) Request failed: {str(e)}"}
    # 응답 처리
    if response.status_code == 200:
        repository = Repository.objects.get(id=repository_id)
        repository.is_apply = False
        repository.save()
        return {"status": "success", "message": f"Webhook(id:{hook_id}) deactivated successfully."}
    else:
        return {"status": "error",
                "message": f"Failed to deactivate webhook(id:{hook_id}): {response.status_code} - {response.text}"}
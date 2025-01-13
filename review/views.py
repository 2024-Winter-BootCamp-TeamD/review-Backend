import json
import os
import re

import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pullrequest.models import FileReview, PRReview
from repository.models import Repository
from user.models import User
from .utils.deepSeekReview import file_code_review

# 리뷰 대상 파일 확장자
SUPPORTED_EXTENSIONS = {".py", ".java", ".jsx", ".js"}


# 리팩토링 요소 정리
## 비동기 처리 구현
## 비동기 처리 구현 이후 웹훅에는 수신 응답 빠르게 반환해야 함
@csrf_exempt
def github_webhook(request):
    if request.method == "POST":
        # JSON 데이터를 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        # PR 이벤트 처리
        try:
            action = data.get('action')  # PR 오픈 / PR 리오픈 / PR 클로즈
            pr = data.get('pull_request')
            if action in ['opened', 'reopened'] and pr:
                sender = data.get('sender', {})
                sender_username = sender.get('login')

                repository_github_id = data.get('repository', {}).get('id')
                if not repository_github_id:
                    return JsonResponse({"message": "Missing repository ID"}, status=400)

                repository = Repository.objects.get(repository_github_id=repository_github_id)
                repo_name = data['repository']['full_name']
                print("repo_name:", repo_name)

                hook_owner = User.objects.get(id=repository.user_id_id)
                review_mode = hook_owner.review_mode
                print(action)
                print(f"Sender's Username: {sender_username}")
                print(f"Hook Owner: {hook_owner}")
                print(f"review mode: {review_mode}")

                pr_number = pr['number']
                print("pr_number:", pr_number)

                access_token = hook_owner.access_token
                print("Access Token:", access_token)

                commit_id = data['pull_request']['head']['sha']

                if sender_username == hook_owner.github_username:
                    pr_review = PRReview(
                        user=hook_owner,
                        title=pr['title'],
                        pr_url=pr['url'],
                        aver_grade="Pending",
                        review_mode=review_mode,
                        al_review="Pending"
                    )
                    pr_review.full_clean()
                    pr_review.save()
                    process_pr_code_review(pr_review, access_token, repo_name, pr_number, commit_id)

                else:
                    process_pr_code_only_review(access_token, repo_name, pr_number, commit_id)

                # 성공적인 응답 반환
                return JsonResponse({
                    "message": "Webhook processed successfully",
                    "action": action,
                    "sender_username": sender_username,
                    "repository_name": repo_name,
                    "pr_number": pr_number,
                }, status=200)

        except Repository.DoesNotExist:
            return JsonResponse({"message": "Repository not found"}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"message": "Hook owner not found"}, status=404)

        except KeyError as e:
            return JsonResponse({"message": f"Missing key: {str(e)}"}, status=400)

    # POST 요청이 아닌 경우
    return HttpResponseBadRequest("Invalid request method")


def get_pr_files(access_token, repo_name, pr_number):
    """
    PR의 모든 파일 정보를 가져오는 함수
    """
    GITHUB_TOKEN = access_token
    GITHUB_API_URL = "https://api.github.com"

    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/files"
    print("get_url:", url)
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve PR files: {response.status_code}, {response.text}")


def download_file_content(file_url):
    """
    파일의 실제 내용을 다운로드하는 함수
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to download file content: {response.status_code}, {response.text}")


def post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, comment):
    """
    PR 파일에 댓글을 추가하는 함수
    """
    GITHUB_TOKEN = access_token
    GITHUB_API_URL = "https://api.github.com"

    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    # 요청 데이터 생성
    data = {
        "body": comment,  # 댓글 내용
        "path": file_path,  # 파일 경로
        "commit_id": commit_id,  # 커밋 ID
        "subject_type": "file",  # 추가된 코드는 RIGHT, 삭제된 코드는 LEFT
    }

    # GitHub API로 댓글 추가 요청
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Comment successfully posted on {file_path}.")
    else:
        print(f"Failed to post comment: {response.status_code}, {response.text}")


def get_grade(score):
    if score in [1, 2]:
        return "D"
    elif score in [3, 4]:
        return "C"
    elif score in [5, 6]:
        return "B"
    elif score in [7, 8]:
        return "A"
    elif score in [9, 10]:
        return "S"
    else:
        return "Unknown"  # 유효하지 않은 점수 처리


def process_pr_code_review(pr_review, access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    익스텐션 사용자의 pr인 경우 db에 저장
    """
    try:
        # PR의 모든 파일 가져오기
        pr_files = get_pr_files(access_token, repo_name, pr_number)

        for file_info in pr_files:
            file_path = file_info["filename"]

            file_extension = os.path.splitext(file_path)[1]

            # 지원하는 확장자인 경우에만 처리
            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                # 파일 내용 가져오기
                file_content = download_file_content(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                store_file_review(file_path, pr_review, review_result)

                # 리뷰 결과를 PR에 댓글로 추가
                post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_result)


            else:
                print(f"Skipping unsupported file: {file_path}")
    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")


def store_file_review(file_path, pr_review, review_result):
    # review 부분 추출
    review_match = re.search(r'"review":\s*"([\s\S]*?)"', review_result)
    if review_match:
        review_text = review_match.group(1)
        print("Review:", review_text)
    else:
        review_text = ""  # review를 찾을 수 없는 경우 기본값
    score_match = re.search(r'"score":\s*"(\d+)"', review_result)
    if score_match:
        score = int(score_match.group(1))  # 숫자로 변환
    else:
        score = 0  # score를 찾을 수 없는 경우 기본값
    grade = get_grade(score)
    print(f"Score: {score}, Grade: {grade}")  # 출력: Score: 7, Grade: A
    file_review = FileReview(
        pr_review=pr_review,
        file_path=file_path,
        comment=review_text,
        grade=grade
    )
    print(f"Score: {score}, Grade: {grade}")  # 출력: Score: 7, Grade: A
    file_review.full_clean()
    file_review.save()


def process_pr_code_only_review(access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    이때 익스텐션 사용자의 pr이 아닌경우 db에 저장하지 않음
    """
    try:
        # PR의 모든 파일 가져오기
        pr_files = get_pr_files(access_token, repo_name, pr_number)

        for file_info in pr_files:
            file_path = file_info["filename"]

            file_extension = os.path.splitext(file_path)[1]

            # 지원하는 확장자인 경우에만 처리
            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                # 파일 내용 가져오기
                file_content = download_file_content(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                # 리뷰 결과를 PR에 댓글로 추가
                post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_result)
            else:
                print(f"Skipping unsupported file: {file_path}")
    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")

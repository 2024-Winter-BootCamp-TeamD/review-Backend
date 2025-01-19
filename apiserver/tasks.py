import os
import re
import requests
from celery import shared_task
from pullrequest.models import PRReview
from review.utils.fileReview import file_code_review
from review.utils.prReview import get_pr_review
from review.utils.common import (
    post_pr_summary_comment, get_grade, get_score_review_text, SUPPORTED_EXTENSIONS, get_problem_type)


@shared_task(max_retries=3)
def async_process_pr_review(pr_review_id, access_token, repo_name, pr_number, commit_id):
    try:
        pr_review = PRReview.objects.get(id=pr_review_id)
        pr_files = async_get_pr_files.delay(access_token, repo_name, pr_number)
        gather_reviews = ""
        total_score = 0
        file_count = 0

        for file_info in pr_files:
            file_path = file_info["filename"]
            file_extension = os.path.splitext(file_path)[1]

            if file_extension in SUPPORTED_EXTENSIONS:
                file_content = async_download_file_content(file_info["raw_url"])
                review_result = file_code_review(file_content, pr_review.id)
                gather_reviews += review_result

                score_match = re.search(r'"score":\s*(\d+)', review_result)
                if score_match:
                    total_score += int(score_match.group(1))
                file_count += 1

                # 댓글 추가
                async_post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_result)

        if file_count > 0:
            average_score = total_score / file_count
            average_grade = get_grade(average_score)
        else:
            average_grade = "Unknown"

        pr_review_result = get_pr_review(gather_reviews, average_grade)
        post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)

    except Exception as e:
        print(f"Error in async_process_pr_code_review: {str(e)}")

@shared_task(max_retries=3)
def async_process_pr_code_only_review(access_token, repo_name, pr_number, commit_id):
    file_num = 0
    total_score = 0
    gather_reviews = ""
    try:
        pr_files = async_get_pr_files(access_token, repo_name, pr_number)

        for file_info in pr_files:
            file_path = file_info["filename"]
            file_extension = os.path.splitext(file_path)[1]

            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                file_num += 1
                file_content = async_download_file_content(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                review_text, score = get_score_review_text(file_path, review_result)
                total_score += score
                gather_reviews += review_text

                # 리뷰 결과를 PR에 댓글로 추가
                async_post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_text)
            else:
                print(f"Skipping unsupported file: {file_path}")

        if file_num > 0:
            aver_score = total_score / file_num
            aver_grade = get_grade(aver_score)
            print("aver_grade:", aver_grade)
            print("gather_reviews:", gather_reviews)

            # 받은 모든 리뷰를 토대로 PR리뷰 받기
            pr_review_result = get_pr_review(gather_reviews, aver_grade)

            #if aver_grade != 'A' and aver_grade != 'S':
            #    problem_type = get_problem_type(pr_review_result)

             #pr에 총평 댓글로 남겨주는 함수 실행
            post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)

    except Exception as e:
        print(f"Error in processing Async-code-only Review: {str(e)}")


@shared_task(max_retries=3)
def async_get_pr_files(access_token, repo_name, pr_number):
    GITHUB_TOKEN = access_token
    GITHUB_API_URL = "https://api.github.com"

    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/files"
    print("get_url:", url)
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

    except requests.RequestException as e:
        print(f"Error in async_get_pr_files: {str(e)}")


@shared_task(max_retries=3)
def async_download_file_content(file_url):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return response.text

    except requests.RequestException as e:
        print(f"Failed to download file content: {response.status_code}, {response.text}")


@shared_task(max_retries=3)
def async_post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, comment):
    if "리뷰할 내용이 없습니다" in comment:
        print(f"Skipping comment for {file_path}: 리뷰할 내용이 없습니다.")
        return

    GITHUB_API_URL = "https://api.github.com"
    url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment,
        "path": file_path,
        "position": 1,
        "commit_id": commit_id
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"Comment successfully posted on {file_path}.")
    except requests.RequestException as e:
        print(f"Failed to post comment: {response.status_code}, {response.json()}")

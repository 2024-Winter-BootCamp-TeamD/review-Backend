import os
import re
import requests
from celery import shared_task
from pullrequest.models import PRReview
from .utils.fileReview import file_code_review
from .utils.prReview import get_pr_review
from review.common import download_file_content, get_grade, store_file_review, get_score_review_text, get_problem_type

# 리뷰 대상 파일 확장자
SUPPORTED_EXTENSIONS = {".py", ".java", ".jsx", ".js"}

@shared_task(ignore_result=True, max_retries=3)
def process_pr_code_only_review(access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    이때 익스텐션 사용자의 pr이 아닌경우 db에 저장하지 않음
    """
    # 등급 평균 추출 준비
    file_num = 0
    total_score = 0
    gather_reviews = ""
    try:
        # PR의 모든 파일 가져오기
        pr_files = get_pr_files(access_token, repo_name, pr_number)

        for file_info in pr_files:
            file_path = file_info["filename"]

            file_extension = os.path.splitext(file_path)[1]

            # 지원하는 확장자인 경우에만 처리
            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                file_num += 1

                # 파일 내용 가져오기
                file_content = download_file_content(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                review_text, score = get_score_review_text(file_path, review_result)
                total_score += score
                gather_reviews += review_text

                # 리뷰 결과를 PR에 댓글로 추가
                post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_text)
            else:
                print(f"Skipping unsupported file: {file_path}")

        if file_num > 0:
            aver_score = total_score / file_num
            aver_grade = get_grade(aver_score)
            print("aver_grade:", aver_grade)
            print("gather_reviews:", gather_reviews)

            # 받은 모든 리뷰를 토대로 PR리뷰 받기
            pr_review_result = get_pr_review(gather_reviews, aver_grade)

            # pr에 총평 댓글로 남겨주는 함수 실행
            post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)
    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")


@shared_task(ignore_result=True, max_retries=3)
def process_pr_code_review(pr_review_id, access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    익스텐션 사용자의 pr인 경우 db에 저장
    """
    try:
        pr_review = PRReview.objects.get(id=pr_review_id)
        # PR의 모든 파일 가져오기
        pr_files = get_pr_files(access_token, repo_name, pr_number)

        # 등급 평균 추출 준비
        file_num = 0
        total_score = 0
        current_avg_score = 0
        gather_reviews = ""

        for file_info in pr_files:
            file_path = file_info["filename"]
            file_extension = os.path.splitext(file_path)[1]

            # 지원하는 확장자인 경우에만 처리
            if file_extension in SUPPORTED_EXTENSIONS:
                print(f"Processing file: {file_path}")

                file_num += 1

                # 파일 내용 가져오기
                file_content = download_file_content(file_info["raw_url"])

                # 코드 리뷰 수행
                review_result = file_code_review(file_content)
                print("review_result:", review_result)

                current_avg_score = total_score / file_num if file_num > 0 else 0

                review_text, score = store_file_review(file_path, pr_review.id, review_result)
                total_score += score
                gather_reviews += review_text
                # 리뷰 결과를 PR에 댓글로 추가
                post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, review_text)
            else:
                print(f"Skipping unsupported file: {file_path}")

        if file_num > 0:
            aver_score = total_score / file_num
            aver_grade = get_grade(aver_score)
            print("aver_grade:", aver_grade)
            print("gather_reviews:", gather_reviews)

            # 받은 모든 리뷰를 토대로 PR리뷰 받기
            pr_review_result = get_pr_review(gather_reviews, aver_grade)

            # pr에 총평 댓글로 남겨주는 함수 실행
            total_review = post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result)

            if aver_grade != 'S':
                problem_type = get_problem_type(pr_review_result)
                if problem_type:
                    pr_review.problem_type = problem_type
                else:
                    print("No problem_type found in pr_review_result.")
            pr_review.total_review = total_review
            pr_review.aver_grade = aver_grade

            pr_review.save()

    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")


@shared_task(ignore_result=True, max_retries=3)
def post_comment_to_pr(commit_id, access_token, repo_name, pr_number, file_path, comment):
    """
    PR 파일에 댓글을 추가하는 함수
    """

    if "리뷰할 내용이 없습니다" in comment:
        print(f"Skipping comment for {file_path}: 리뷰할 내용이 없습니다.")
        return

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


@shared_task(max_retries=3)
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


@shared_task(max_retries=3)
def post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result):
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    # review 부분 추출
    total_review_match = re.search(r'"total_review":\s*"([\s\S]*?)"', pr_review_result)
    if total_review_match:
        total_review_text = total_review_match.group(1)
        print("total_review:", total_review_text)
    else:
        total_review_text = ""  # total_review를 찾을 수 없는 경우 기본값

    problem_type_match = re.search(r'"problem_type":\s*"([^"]*?)"', pr_review_result)
    if problem_type_match:
        problem_type_text = problem_type_match.group(1)
        print("problem_type:", problem_type_text)
    else:
        problem_type_text = ""

    # average_grade 부분 추출
    average_grade_match = re.search(r'"average_grade":\s*"([^"]*?)"', pr_review_result)
    if average_grade_match:
        average_grade_text = average_grade_match.group(1)
        print("average_grade:", average_grade_text)
    else:
        average_grade_text = ""

    comment_body = f"""
    ### PR 리뷰 총평
    - **총평**: {total_review_text}
    - **문제 유형**: {problem_type_text}
    - **평균 등급**: {average_grade_text}
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment_body.strip()  # 총평 내용
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴
        print("PR에 총평 댓글이 성공적으로 작성되었습니다.")
    except requests.exceptions.RequestException as e:
        print(f"PR 댓글 작성 중 오류 발생: {str(e)}")

    return total_review_text
import os
import time
import requests
from celery import shared_task, group, chain
from pullrequest.models import PRReview, FileReview
from .utils.fileReview import file_code_review
from .utils.prReview import get_pr_review
from review.common import download_file_content, get_grade, get_score_review_text, get_problem_type, \
    extract_pattern, format_review, update_pr_status

# 리뷰 대상 파일 확장자
SUPPORTED_EXTENSIONS = {".py", ".java", ".jsx", ".js"}

# 시간 제한
TIMEOUT_SECONDS = 3

@shared_task(ignore_result=True, max_retries=3)
def process_only_code_review(review_mode, access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    이때 익스텐션 사용자의 pr이 아닌경우 db에 저장하지 않음
    """
    try:
        # PR의 모든 파일 가져오기, 필터링
        pr_files = get_pr_files(access_token, repo_name, pr_number)
        valid_files = [
            file_info for file_info in pr_files
            if os.path.splitext(file_info["filename"])[1] in SUPPORTED_EXTENSIONS
        ]
        if not valid_files:
            print("No valid files to process.")
            return

        # 파일 리뷰 태스크 병렬 실행
        file_review_tasks = group(
            run_only_file_review.s(file_info, review_mode, access_token, repo_name, pr_number, commit_id)
            for file_info in valid_files
        )

        # 파일 리뷰 결과를 PR 리뷰 태스크로 전달
        chain(
            file_review_tasks |
            skip_pr_review_if_timeout.s(access_token, repo_name, pr_number) |
            run_only_pr_review.s(review_mode, access_token, repo_name, pr_number, commit_id)
        ).apply_async()
    except Exception as e:
        print(f"Error in process_pr_code_review: {str(e)}")


@shared_task(ignore_result=True, max_retries=3)
def process_code_review(pr_review_id, access_token, repo_name, pr_number, commit_id):
    """
    PR의 모든 파일에 대해 코드 리뷰를 수행하고, 결과를 PR에 댓글로 작성하는 함수
    익스텐션 사용자의 pr인 경우 db에 저장
    """
    try:
        # PR의 모든 파일 가져오기, 필터링
        pr_files = get_pr_files(access_token, repo_name, pr_number)
        valid_files = [
            file_info for file_info in pr_files
            if os.path.splitext(file_info["filename"])[1] in SUPPORTED_EXTENSIONS
        ]
        if not valid_files:
            print("No valid files to process.")
            return

        # 파일 리뷰 태스크 병렬 실행
        file_review_tasks = group(
            run_file_review.s(file_info, pr_review_id, access_token, repo_name, pr_number, commit_id)
            for file_info in valid_files
        )

        # 파일 리뷰 결과를 PR 리뷰 태스크로 전달
        chain(
            file_review_tasks |
            skip_pr_review_if_timeout.s(access_token, repo_name, pr_number) |
            run_pr_review.s(pr_review_id, access_token, repo_name, pr_number, commit_id)
        ).apply_async()

    except Exception as e:
        print(f"Error in process_code_review: {str(e)}")


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
def run_file_review(file_info, pr_review_id, access_token, repo_name, pr_number, commit_id):
    try:
        start_time = time.time()
        file_path = file_info["filename"]
        file_content = download_file_content(file_info["raw_url"])
        pr_review = PRReview.objects.get(id=pr_review_id)
        review_mode = pr_review.review_mode

        # AI API를 사용하여 파일 리뷰 수행
        review_result = file_code_review(review_mode, file_content)

        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT_SECONDS:
            print(f"Timeout: Skipping file review for {file_path}.")
            return None

        review_text, score = get_score_review_text(review_result)
        # 파일 리뷰 저장
        file_review = FileReview(
            pr_review=pr_review,
            file_path=file_path,
            comment=review_text,
            grade=get_grade(score),
        )
        file_review.full_clean()
        file_review.save()

        # PR 파일 리뷰 결과를 댓글로 추가
        comment_data = {
            "review_mode": review_mode,
            "commit_id": commit_id,
            "access_token": access_token,
            "repo_name": repo_name,
            "pr_number": pr_number,
            "file_path": file_path,
            "comment": review_text,
            "score": score,
        }
        post_comment_to_pr(comment_data)
        return {"score": score, "review_text": review_text}

    except Exception as e:
        print(f"Error in process_file_review for file {file_info['filename']}: {str(e)}")

@shared_task(max_retries=3)
def run_only_file_review(file_info, review_mode, access_token, repo_name, pr_number, commit_id):
    try:
        start_time = time.time()
        file_path = file_info["filename"]
        file_content = download_file_content(file_info["raw_url"])

        # AI API를 사용하여 파일 리뷰 수행
        review_result = file_code_review(review_mode, file_content)

        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT_SECONDS:
            print(f"Timeout: Skipping file review for {file_path}.")
            return None

        review_text, score = get_score_review_text(review_result)

        comment_data = {
            "review_mode": review_mode,
            "commit_id": commit_id,
            "access_token": access_token,
            "repo_name": repo_name,
            "pr_number": pr_number,
            "file_path": file_path,
            "comment": review_text,
            "score": score,
        }

        # PR 파일 리뷰 결과를 댓글로 추가
        post_comment_to_pr.delay(comment_data)
        return {"score": score, "review_text": review_text}

    except Exception as e:
        print(f"Error in process_file_review for file {file_info['filename']}: {str(e)}")



@shared_task(ignore_result=True, max_retries=3)
def post_comment_to_pr(comment_data):
    """
    PR 파일에 댓글을 추가하는 함수
    """
    comment = comment_data["comment"]
    file_path = comment_data["file_path"]
    score = int(comment_data["score"])
    review_mode = comment_data["review_mode"]
    if "리뷰할 내용이 없습니다" in comment:
        print(f"Skipping comment for {file_path}: 리뷰할 내용이 없습니다.")
        return

    # 리뷰 텍스트 포맷팅
    formatted_comment = format_review(comment)

    GITHUB_TOKEN = comment_data['access_token']
    GITHUB_API_URL = "https://api.github.com"

    url = f"{GITHUB_API_URL}/repos/{comment_data['repo_name']}/pulls/{comment_data['pr_number']}/comments"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

    # 요청 데이터 생성
    data = {
        "body": f"**Mode**: {review_mode}\n"
                f"**Score**: {score} / 10\n"
                f"**Grade**: {get_grade(score)}\n\n"
                f"{formatted_comment}",  # 줄바꿈 처리된 리뷰 본문
        "path": file_path,  # 파일 경로
        "commit_id": comment_data['commit_id'],  # 커밋 ID
        "subject_type": "file",  # 추가된 코드는 RIGHT, 삭제된 코드는 LEFT
    }
    # GitHub API로 댓글 추가 요청
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Comment successfully posted on {file_path}.")
    else:
        print(f"Failed to post comment: {response.status_code}, {response.text}")



@shared_task(max_retries=3)
def skip_pr_review_if_timeout(file_review_results, access_token, repo_name, pr_number):
    """
    모든 파일 리뷰가 타임아웃되었는지 확인 후 PR 리뷰를 중단, 메시지를 GitHub에 직접 작성
    """
    if not file_review_results or all(result is None for result in file_review_results):
        print("All file reviews skipped due to timeout. Skipping PR review.")

        # GitHub API로 타임아웃 메시지 댓글 작성
        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.post(url, headers=headers, json={
                "body": f"**타임아웃 경고**: AI API 응답 시간이 초과되어 파일 리뷰가 중단되었습니다.",
            })
            if response.status_code == 201:
                print(f"Timeout comment successfully posted.")
            else:
                print(f"Failed to post timeout comment: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error posting timeout comment: {str(e)}")

        return None  # Celery 체인 중단

    return file_review_results



# PR 리뷰 수행
@shared_task(ignore_result=True, max_retries=3)
def run_pr_review(file_review_results, pr_review_id, access_token, repo_name, pr_number, commit_id):
    try:
        pr_review = PRReview.objects.get(id=pr_review_id)
        review_mode = pr_review.review_mode
        # 파일 리뷰 결과 집계
        total_score = sum(result["score"] for result in file_review_results if result)
        aver_grade = get_grade(total_score // len(file_review_results))
        gather_reviews = "".join(result["review_text"] for result in file_review_results if result)

        # PR 총평 생성
        pr_review_result = get_pr_review(gather_reviews, review_mode)

        # PR 총평 댓글 추가
        total_review = post_pr_summary_comment(
            access_token, repo_name, pr_number, pr_review_result, review_mode, aver_grade
        )

        # PRReview 업데이트
        pr_review.total_review = total_review
        pr_review.aver_grade = aver_grade

        # 문제 유형 추출
        # if aver_grade != 'S': 프론트에서 하기로
        problem_type = get_problem_type(pr_review_result)
        if problem_type:
            pr_review.problem_type = problem_type

        pr_review.save()
        print(f"PRReview 업데이트 완료: {pr_review}")

        # 등급에 따라 상태 업데이트
        state = "failure" if aver_grade.strip() in {"B", "C", "D"} else "success"
        description = "PR 평균 등급이 기준 이하입니다." if state == "failure" else "PR이 품질 기준을 충족합니다."

        # 디버깅 출력
        print(f"PR 상태 설정: {state}, 평균 등급: {aver_grade}")

        update_pr_status(
            repo_name=repo_name,
            sha=commit_id,
            state=state,
            description=description,
            context="Code Quality Check",
            access_token=access_token,
        )
        print(f"PR 리뷰 상태 업데이트 완료: {state}, 등급: {pr_review.aver_grade}")

    except PRReview.DoesNotExist:
        print(f"PRReview with ID {pr_review_id} does not exist.")
    except Exception as e:
        print(f"Error in aggregate_and_finalize_pr_review: {e}")


# PR 리뷰 수행
@shared_task(ignore_result=True, max_retries=3)
def run_only_pr_review(file_review_results, review_mode, access_token, repo_name, pr_number, commit_id):
    try:
        # 파일 리뷰 결과 집계
        total_score = sum(result["score"] for result in file_review_results if result)
        aver_grade = get_grade(total_score // len(file_review_results))
        gather_reviews = "".join(result["review_text"] for result in file_review_results if result)

        # PR 총평 생성
        pr_review_result = get_pr_review(gather_reviews, review_mode)

        # PR 총평 댓글 추가
        post_pr_summary_comment(
            access_token, repo_name, pr_number, pr_review_result, review_mode, aver_grade
        )

        # 등급에 따라 상태 업데이트
        state = "failure" if aver_grade.strip() in {"B", "C", "D"} else "success"
        description = "PR 평균 등급이 기준 이하입니다." if state == "failure" else "PR이 품질 기준을 충족합니다."

        # 디버깅 출력
        print(f"PR 상태 설정: {state}, 평균 등급: {aver_grade}")

        update_pr_status(
            repo_name=repo_name,
            sha=commit_id,
            state=state,
            description=description,
            context="Code Quality Check",
            access_token=access_token,
        )
        print(f"PR 리뷰 상태 업데이트 완료: {state}, 등급: {aver_grade}")

    except Exception as e:
        print(f"Error in process_only_pr_review: {e}")



@shared_task(max_retries=3)
def post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result, review_mode, aver_grade):
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"

    # Extract review data
    total_review = extract_pattern(
        r'"total_review":\s*"([\s\S]*?)"', pr_review_result, ""
    ).replace("```", "").strip()  # 백틱 제거
    problem_type = extract_pattern(
        r'"problem_type":\s*"([^"]*?)"', pr_review_result, ""
    )

    # Format the total review (split into readable lines)
    formatted_total_review = format_review(total_review)

    # Compose the comment body
    comment_body = f"""
## 📝 PR 리뷰 총평

### 🔍 **총평**
{formatted_total_review}

### 🚩 **주요 문제 유형**
- {problem_type or "특별한 문제 유형이 없습니다."}

### 📊 **모드 및 평균 등급**
- 리뷰 모드: {review_mode or "모드 정보 없음"}
- 평균 등급: {aver_grade or "평가 점수 없음"}

---
💡 **Tip**: '{problem_type or "개선 사항"}'에 대한 개선점을 중점적으로 고려하세요.
    """.strip()  # 전체 텍스트 양 끝의 공백 제거

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "body": comment_body.strip()
    }

    try:
        # Check final comment body before sending
        print("Final Comment Body Sent to GitHub:")
        print(comment_body)

        # Post to GitHub
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("PR에 총평 댓글이 성공적으로 작성되었습니다.")
    except requests.exceptions.RequestException as e:
        print(f"PR 댓글 작성 중 오류 발생: {str(e)}")

    return formatted_total_review


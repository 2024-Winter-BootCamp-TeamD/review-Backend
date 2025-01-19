import json
import re
import requests

from pullrequest.models import FileReview

# 리뷰 대상 파일 확장자
SUPPORTED_EXTENSIONS = {".py", ".java", ".jsx", ".js"}

def get_grade(score):
    if isinstance(score, (int, float)):  # 정수 또는 실수인지 확인
        if 91 <= score <= 100:
            return "S"
        elif 71 <= score <= 90:
            return "A"
        elif 51 <= score <= 70:
            return "B"
        elif 31 <= score <= 50:
            return "C"
        elif 0 <= score <= 30:
            return "D"
    else:
        return "Invalid"  # 정수 또는 실수가 아닌 경우

def post_pr_summary_comment(access_token, repo_name, pr_number, pr_review_result):
    """
    PR 전체 리뷰를 댓글로 추가
    """
    GITHUB_API_URL = "https://api.github.com"
    url = f"{GITHUB_API_URL}/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 응답 데이터 클린업
        # 백틱(```)과 첫 줄에 포함된 "json" 제거
        clean_result = pr_review_result.strip("```").strip()
        if clean_result.startswith("json"):
            clean_result = clean_result.split("\n", 1)[1].strip()  # 첫 줄 제거

        print(f"Cleaned PR Review Result:\n{clean_result}")

        # JSON 파싱
        pr_review_data = json.loads(clean_result)

        # `summary` 추출
        total_review_text = pr_review_data.get("summary", "총평 생성 실패.")
        print("Total Review Text:", total_review_text)

        # GitHub API 요청 데이터 생성
        data = {"body": total_review_text}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            print("PR에 총평 댓글이 성공적으로 작성되었습니다.")
        else:
            print(f"Failed to post summary comment: {response.status_code}, {response.text}")

        return total_review_text

    except json.JSONDecodeError as e:
        print(f"Failed to parse PR review result as JSON: {str(e)}")
        return "총평 생성 실패."
    except Exception as e:
        print(f"Error in post_pr_summary_comment: {str(e)}")
        return "총평 생성 실패."

def get_problem_type(pr_review_result):
    problem_type_match = re.search(r'"problem_type":\s*"([^"]*)"', pr_review_result)
    print("problem_type:", problem_type_match.group(1))
    return problem_type_match.group(1)


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
    file_review = FileReview(
        pr_review=pr_review,
        file_path=file_path,
        comment=review_text,
        grade=grade
    )
    print(f"Score: {score}, Grade: {grade}")  # 출력: Score: 7, Grade: A
    file_review.full_clean()
    file_review.save()

    return review_text, score


def get_score_review_text(file_path, review_result):
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

    return review_text, score
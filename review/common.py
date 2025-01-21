import json
import re
import requests
from pullrequest.models import FileReview, PRReview


def download_file_content(file_url):
    """
    파일의 실제 내용을 다운로드하는 함수
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to download file content: {response.status_code}, {response.text}")


def get_grade(score):
    if isinstance(score, (int, float)):  # 정수 또는 실수인지 확인
        if 1 <= score < 3:
            return "D"
        elif 3 <= score < 5:
            return "C"
        elif 5 <= score < 7:
            return "B"
        elif 7 <= score < 9:
            return "A"
        elif 9 <= score <= 10:
            return "S"
        else:
            return "Unknown"  # 1 미만 또는 10 초과인 경우
    else:
        return "Unknown"  # 정수 또는 실수가 아닌 경우


def get_problem_type(pr_review_result):
    try:
        # JSON 파싱
        review_data = json.loads(pr_review_result)

        # problem_type 추출
        problem_type = review_data.get("problem_type", None)

        if problem_type:
            print("problem_type:", problem_type)
            return problem_type
        else:
            print("problem_type not found.")
            return None
    except json.JSONDecodeError:
        print("Invalid JSON format. Falling back to regex.")

    problem_type_match = re.search(r'"problem_type":\s*"([^"]*)"', pr_review_result)
    if problem_type_match:
        problem_type = problem_type_match.group(1)
        print("problem_type (from regex):", problem_type)
        return problem_type
    else:
        print("problem_type not found in regex.")
        return None


def store_file_review(file_path, pr_review_id, review_result, current_avg_score=0, file_num=0):
    # review 부분 추출
    pr_review = PRReview.objects.get(id=pr_review_id)
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
        if file_num > 0:
            score = current_avg_score
            print(f"Score not found. Using current average score: {score}")
        else:
            score = 5
            print(f"Score not found. Using default score: {score}")
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
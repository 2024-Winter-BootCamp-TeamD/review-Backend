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


def get_problem_type(pr_review_result):
    try:
        # JSON 파싱, problem_type 추출
        review_data = json.loads(pr_review_result)
        problem_type = review_data.get("problem_type", None)

        if problem_type:
            print("problem_type:", problem_type)
            return problem_type
        else:
            print("problem_type not found.")
            return None
    except json.JSONDecodeError:
        print("Invalid JSON format. Falling back to regex.")

    return extract_pattern(r'"problem_type":\s*"([^"]*)"', pr_review_result)


# review에서 text와 score 추출
def get_score_review_text(review_result):
    review_text = extract_pattern(r'"review":\s*"([\s\S]*?)"', review_result, "")
    print("Review:", review_text)

    score = int(extract_pattern(r'"score":\s*"(\d+)"', review_result, 5))
    print(f"Score: {score}")  # 출력: Score: 7, Grade: A

    return review_text, score


def extract_pattern(pattern, text, default=None):
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # 매칭된 그룹에 변환 함수 적용
    return default

"""
정규식을 사용해 텍스트에서 패턴을 추출하고, 추출된 값에 변환 적용

pattern: 검색할 정규식 패턴
    text: 검색 대상 텍스트
    default: 패턴이 발견되지 않을 경우 반환할 기본값
    transform: 추출된 값에 적용할 변환 함수 (기본값은 그대로 반환)
   
 
value = extract_pattern(
    pattern=r'"problem_type":\s*"([\s\S]*?)"',
    text=json_string,
    default="",
    transform=lambda x: x.strip()  # 공백 제거
)
"""
import json
import re
import requests


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
    grade_mapping = {
        1: "D", 2: "D",
        3: "C", 4: "C",
        5: "B", 6: "B",
        7: "A", 8: "A",
        9: "S", 10: "S",
    }
    return grade_mapping.get(score, "Unknown")


def get_problem_type(pr_review_result):
    try:
        # JSON 파싱
        review_data = json.loads(pr_review_result)
        problem_type = review_data.get("problem_type", None)

        if problem_type:
            print("problem_type:", problem_type)
        else:
            print("problem_type not found.")

    except json.JSONDecodeError:
        problem_type = extract_pattern(r'"problem_type":\s*"([^"]*)"', pr_review_result)
        print("Invalid JSON format. problem_type(regex):", problem_type)

    return problem_type


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
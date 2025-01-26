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



def sanitize_code_snippet(code_snippet):
    if not code_snippet:
        return ""
    # 역슬래시(`\`)와 기타 특수 문자를 Markdown-safe 형태로 변환
    sanitized = (
        code_snippet.replace("\\", "\\\\")  # 역슬래시를 임시 대체
        .replace("`", "\\`")  # 백틱을 이스케이프 처리
        .replace("\n", "\\n")  # 줄바꿈을 JSON-safe 형태로 변환
    )
    return sanitized



def restore_code_snippet(sanitized_snippet):
    if not sanitized_snippet:
        return ""
    return (
        sanitized_snippet.replace("\\\\", "\\")  # 역슬래시 복원
        .replace("\\n", "\n")  # 줄바꿈 복원
        .replace("\\`", "`")  # 백틱 복원
    )



def format_review(review_text, line_length=150):
    if not review_text:
        return "리뷰 내용이 없습니다."

    formatted_lines = []
    in_code_block = False

    for line in review_text.split("\\n"):  # JSON에서 줄바꿈 분리
        # 코드 블록 시작/끝 감지
        if line.startswith("```python") or line.startswith("```"):
            in_code_block = not in_code_block
            formatted_lines.append(line)
            continue

        if in_code_block:
            # 코드 블록 내 특수 문자 변환
            sanitized_line = sanitize_code_snippet(line)
            formatted_lines.append(sanitized_line)
        else:
            # 코드 블록 외부에서는 기본 줄바꿈 처리
            words = line.split(" ")
            current_line = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 > line_length:
                    formatted_lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1

            if current_line:
                formatted_lines.append(" ".join(current_line))

    formatted_text = "\n".join(formatted_lines)
    return restore_code_snippet(formatted_text)



def update_pr_status(repo_name, sha, state, description, context, access_token):
    """
    PR 상태를 업데이트하는 함수.
    """
    url = f"https://api.github.com/repos/{repo_name}/statuses/{sha}"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "state": state,  # "success", "failure", or "pending"
        "description": description,
        "context": context,
    }
    print(f"GitHub 상태 업데이트 요청: {data}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"PR 상태 업데이트 성공: {state}")
    else:
        print(f"PR 상태 업데이트 실패: {response.status_code}, {response.text}")



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
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def get_mode_prompts(review_mode):
    mode_prompts = {
        "clean": ["명명 규칙", "재사용성", "단일 책임 원칙", "캡슐화"],
        "optimize": ["시간복잡도", "공간복잡도", "알고리즘 적합성", "자료 구조 적합성"],
        "basic": ["코드 가독성", "에러 처리", "코드 주석 작성", "테스트 케이스 작성"],
        "newbie": ["기본 자료형 사용", "조건문 작성", "반복문 작성", "함수 정의 연습"],
        "study": ["문제 해결 전략", "최적화 가능성 분석", "알고리즘 설계", "데이터 구조 선택"]
    }
    return mode_prompts.get(review_mode, ["지원되지 않는 모드입니다."])


def get_pr_review(review, aver_grade, review_mode):
    try:
        mode_criteria = get_mode_prompts(review_mode)
        mode_criteria_str = ", ".join(mode_criteria)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f'''
                            당신은 **코드리뷰** 전문 개발자로, 
                            GitHub PR의 수정된 파일에 대해 작성된 코드리뷰들을 보고 종합한 PR 총평을 제공하는 일을 한다.

            ## 입력 데이터
            - 리뷰 내용: {review}
            - 평균 등급: {aver_grade}
            - 리뷰 모드: {review_mode}

            ## 규칙
            ** 모든 리뷰 내용을 세세히 검토하여 총평을 작성한다. 총평은 다음과 같은 형식으로 작성해야 한다:
            - 총평은 전반적인 평가와 개선사항을 포함한다.
            - 전반적인 평가를 작성한 후, 개선사항은 아래와 같이 숫자로 나열하며 명확히 제시한다.
            - 개선사항의 각 항목은 새로운 줄로 작성하며, 마크다운 형식에서 줄바꿈이 적용되도록 한다.
            - 형식 예시:
              ```
              전반적으로 코드는 잘 작성되어 있으며, 가독성과 안정성이 높습니다. 그러나 몇 가지 개선할 점이 있습니다:
              1. SECRET_KEY가 하드코딩되어 있으므로 환경 변수로 관리하는 것이 좋습니다.
              2. DEBUG 모드는 프로덕션 환경에서 반드시 False로 설정해야 합니다.
              3. 주석을 추가하여 코드의 가독성을 높이는 것을 권장합니다.
              ```

            - 평균 등급이 S인 경우 problem_type을 출력하지 않는다.
            - **problem_type**: 평균 등급이 D, C, B, A라면 {mode_criteria_str} 중 가장 중요한 문제를 선택하여 지정한다.
            - **total_review**: 위의 규칙에 따라 작성된 총평 내용을 출력한다.

            ## 출력 형식
            출력 형식은 JSON 형태로 작성한다. 답안은 JSON 형식만 포함하며, 다음의 키를 포함한다:
            [
                "average_grade": "평균 등급 값",
                "problem_type": "가장 주요한 문제 유형",
                "review_mode": "{review_mode}",
                "total_review": "총평 내용"
            ]
                        '''},
            ],
            stream=False
        )
        pr_review = response.choices[0].message.content
        print("pr_review: ", response.choices[0].message.content)
        return pr_review

    except Exception as e:
        print(f"Error in making pr_review: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})

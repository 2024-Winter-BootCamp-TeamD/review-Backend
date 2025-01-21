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
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f'''
                    당신은 **코드리뷰** 전문 개발자로, 
                    하나의 PR의 수정된 파일들에 대해 작성된 각각의 코드리뷰들을 보고 종합한 PR 총평을 만들어주는 일을 한다.
    ##규칙
    ** {review}의 리뷰들을 세세히 검토하며, 해당 리뷰들을 아우르는 총평을 만든다.
    - **total_review**: 당신이 받은 모든 리뷰들을 종합하여 총평을 만든다. {review_mode}에 맞는 심사 기준에 따라 리뷰를 진행한다.
    - **problem_type**: 만약 평균 등급이 D,C,B,A 라면 문제를 찾고, 사용자의 모드가 "{review_mode}"일 때 다음 기준 중 하나를 선택한다:
        {", ".join(mode_criteria)}
      - 평균 등급이 S인 경우 problem_type은 출력하지 않는다.

    ## 출력 형식
    출력 형식은 JSON 형태로 각 key는 다음과 같이 구성한다. 
    답안은 [] 내부에 작성되어야 하며, JSON 형식으로만 출력한다.
    [
        "total_review": " ",
        "problem_type": " " ,
        "average_grade": " ",
    ]

    ## 입력 데이터
    - 리뷰 내용: {review}
    - 평균 등급: {aver_grade}
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
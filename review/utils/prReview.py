import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


# def file_code_review(code, review_mode, prompt): # 나중에 모드 여러개 프롬프트 만들면 수정
def get_pr_review(review, aver_grade):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f'''
                    당신은 **코드리뷰** 전문 개발자 입니다. 
    당신의 임무는 하나의 PR의 수정된 파일들에 대해 작성된 각각의 코드리뷰들을 종합한 PR 총평을 만들어주는 것입니다.
    ##규칙
    ** {review}의 리뷰들을 세세히 검토하며, 해당 리뷰들을 아우르는 총평을 만든다.
    - **total_review**: 모든 리뷰를 종합한 총평
    - **problem_type**: 평균 등급이 D,C,B,A 라면 문제가 있다고 판단하여, 당신에게 넘겨준 리뷰들의 가장 큰 문제 하나를
    "명명 규칙": "clean",
    "재사용성": "clean",
    "단일 책임 원칙": "clean",
    "캡슐화": "clean",
    "시간복잡도": "optimize",
    "공간복잡도": "optimize",
    "알고리즘 적합성": "optimize",
    "자료 구조 적합성": "optimize",
    "코드 가독성": "basic"
    "에러 처리": "basic"
    "코드 주석 작성": "basic"
    "테스트 케이스 작성": "basic"
    "기본 자료형 사용": "new bie"
    "조건문 작성": "new bie"
    "반복문 작성": "new bie"
    "함수 정의 연습": "new bie"
    "문제 해결 전략": "study"
    "최적화 가능성 분석": "study"
    "알고리즘 설계": "study"
    "데이터 구조 선택": "study"
    중 골라서 키워드 problem_type으로 지정해주세요 앞의 단어가 problem_type이고 뒤의 단어는 사용자의 모드 입니다.
    - 키워드의 종류는 모드 별로 4개씩 존재합니다. 사용자가 선택한 모드에 맞게 골라진 키워드를 problem_type으로 지정하세요.

        - 평균 등급이 S인경우 problem_type은 아예 출력하지 마세요
    ## 출력 형식
    출력 형식은 JSON 형태로 각 key는 다음과 같이 구성되어야 합니다. 
    답안은 [] 내부에 작성되어야 하며, JSON 형태로만 제공합니다.
    [
        "total_review": " ",
        "problem_type": " " ,
        "average_grade": " ",
    ]
    ## 질문
    - 당신에게 넘겨주는 모든 리뷰들을 종합해 해당 PullRequest의 총평을 만들어주세요

    ## 입력 데이터
    - 코드: {review}
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
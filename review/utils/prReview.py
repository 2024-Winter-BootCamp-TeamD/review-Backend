import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from review.utils.prompts import newbiePrompt

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
    당신의 임무는 하나의 PR의 수정된 파일들에 대해 작성된 각각의 코드리뷰들을 보고 종합한 PR 총평을 만들어주는 것입니다.
    ##규칙
    ** {review}의 리뷰들을 세세히 검토하며, 해당 리뷰들을 아우르는 총평을 만들어줘야 합니다.
    - **total_review**: 당신에게 넘겨준 모든 리뷰들을 종합하여 총평을 만들어주세요
    - **problem_type**: 만약 평균 등급이 D,C,B라면 문제가 있다고 판단하여, 당신에게 넘겨준 리뷰들의 가장 큰 문제 하나를 키워드로 생성해 problem_type으로 지정해주세요
        - 평균 등급이 A,S인경우 problem_type은 아예 출력하지 마세요
    ## 출력 형식
    출력 형식은 JSON 형태로 각 key는 다음과 같이 구성되어야 합니다. 
    답안은 [] 내부에 작성되어야 하며, JSON 형태로만 제공합니다.
    [
        "total_review": " ",
        "problem_type": " " ,
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
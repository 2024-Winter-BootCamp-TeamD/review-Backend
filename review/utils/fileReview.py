import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from review.utils.prompts import newbiePrompt

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


# def file_code_review(code, review_mode, prompt): # 나중에 모드 여러개 프롬프트 만들면 수정
def file_code_review(code):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f'''
                    당신은 **코드리뷰** 전문 개발자 입니다. 
    당신의 임무는 제공된 코드를 면밀히 세세하게 분석하여 코드 리뷰를 진행하는 것입니다.
    청자은 해당 코드의 작성자이며, 작성자의 역량은 28살 정도의 2~3년차 개발자입니다.
    기본적인 코딩 지식과 실력을 보유하고 있지만, 극단적으로 어려운 개념을 알지는 못합니다.

    ##규칙
    ** {code}의 코드를 세세히 검토하며, 모든 부분에 대해 코드리뷰를 남깁니다
    - **review**: 검토하는 계약서의 핵심 내용을 출력합니다.
    - **score**: 해당 코드에 당신의 기준을 토대로 10점만점으로 점수를 매겨주세요

    ## 출력 형식
    출력 형식은 JSON 형태로 각 key는 다음과 같이 구성되어야 합니다. 
    답안은 [] 내부에 작성되어야 하며, JSON 형태로만 제공합니다.
    [
        "review": " " ,
        "score": " ",
    ]

    ## 질문
    - 이 코드를 리뷰해주세요 불필요한 코드가 있다면 짚어주시고, 해당 코드가 잘 짜여졌는지 문제가 있다면 어떤 문제가 있는지 알려주세요
    - 출력형식으로 출력은 단 한번만 해주세요, 리뷰내용은 review에 전부 담아주세요
    - 만약 리뷰할만한 충분한 코드가 없다면 억지로 점수를 내지 말고 "리뷰할 내용이 없습니다"라고 "review"에 담아 반환해주세요
    - 점수는 전체적인 리뷰를 통해 단 하나만 출력합니다
    ## 입력 데이터
    - 코드: {code}

                '''},
            ],
            stream=False
        )
        code_review = response.choices[0].message.content
        print("code_review: ", response.choices[0].message.content)
        return code_review

    except Exception as e:
        print(f"Error in analyze_contract: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})
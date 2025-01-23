import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from review.utils.prompts import newbiePrompt, cleanPrompt

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def get_mode_concept(review_mode):
    mode_concepts = {
        "clean": cleanPrompt,
        "optimize": "성능 최적화 최우선 모드. 시간복잡도, 공간복잡도 등의 성능 가치를 최우선에 두고 평가와 개선 방안 제공.",
        "basic": "코드 리뷰",
        "newbie": "코딩을 잘 모르는 초보자 기준 모드. 초보자의 눈높이에 맞춰 쉬운 용어를 사용하는 설명 제공.",
        "study": "문제 해결 전략, 최적화 가능성 분석, 알고리즘 설계, 데이터 구조 선택 등 학습자를 위한 조언"
    }
    return mode_concepts.get(review_mode, ["지원되지 않는 모드입니다."])

# def file_code_review(code, review_mode, prompt): # 나중에 모드 여러개 프롬프트 만들면 수정
def file_code_review(review_mode, code):
    try:
        mode_concept = get_mode_concept(review_mode)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f'''
    당신은 **코드리뷰** 전문 개발자로, 제공된 코드를 면밀히 세세하게 분석하여 코드 리뷰를 진행하는 일을 한다.

    ## 입력 데이터
    - 코드: {code}
    
    ##규칙
    ** 입력 데이터 코드를 세세히 검토하며, 모든 부분에 대해 코드 리뷰를 남긴다. 출력은 단 한 번만 한다.
    ** 리뷰할 만한 충분한 코드가 없다면 억지로 점수를 내지 말고 "리뷰할 내용이 없습니다"라고 "review"에 담아 반환한다.
    - **score**: 코드에 10점 만점 기준으로 점수를 매긴다. 단 하나의 점수만 제공한다.
    - **review**: {mode_concept} 컨셉에 맞춰 리뷰를 제공한다.
    
    ## 리뷰 형식 안내
    - 리뷰에서 항목별로 나누어 작성할 때는, 예: "1) 첫째 ... 2) 둘째 ... 3) 셋째 ..."
    - 실제 개행문자(\\n)나 백틱(`)은 사용하지 않는다.
    - 대신 항목 간 구분을 위해 "[n]" 과 같은 특수 문자로 줄바꿈을 표시한다.
    예: "1) 첫째 [n]2) 둘째 [n]3) 셋째 ...

    ## 출력 형식
    출력 형식은 JSON 형태로 각 key는 다음과 같이 구성한다.
    답안은 [] 내부에 작성하고, JSON 형태로만 제공한다.
    항목 간 줄바꿈을 추가하여 가독성을 높입니다
    [
        "score": " ",
        "review": " ",
    ]
    - JSON 바깥에 텍스트를 출력하지 않는다.
    - 개행 문자(\n)와 벡틱(`)등을 내용에 절대 포함하지 않는다.
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
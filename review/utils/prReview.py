import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from review.utils.prompts.cleanPrompt import GUIDELINE_PROMPT as CLEAN_PROMPT

# 환경 변수 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def get_pr_review(review, aver_grade, review_mode="clean"):
    """
    PR 총평 생성 함수
    - review: PR 리뷰 내용
    - aver_grade: 평균 등급
    - review_mode: 리뷰 모드 (기본값: clean mode)
    """
    try:
        # 프롬프트 준비
        if review_mode == "clean":
            prompt = CLEAN_PROMPT.format(review=review, aver_grade=aver_grade)
        else:
            raise ValueError(f"Invalid review mode: {review_mode}")

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt}],
            stream=False,
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_pr_review: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})


# def get_pr_review(review, aver_grade, review_mode="clean"):
#     """
#     PR 전체 리뷰 생성 함수.
#     - review: PR 리뷰 내용.
#     - aver_grade: 평균 등급.
#     - review_mode: 리뷰 모드 ('clean', 'optimize'). 기본값은 'clean'.
#     """
#     try:
#         # 프롬프트 선택
#         if review_mode == "clean":
#             prompt = CLEAN_PROMPT.format(review=review, aver_grade=aver_grade)
#         elif review_mode == "optimize":
#             prompt = OPTIMIZE_PROMPT.format(review=review, aver_grade=aver_grade)
#         else:
#             raise ValueError(f"Invalid review mode: {review_mode}")
#
#         # OpenAI API 호출
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[{"role": "system", "content": prompt}],
#             stream=False,
#         )
#         return response.choices[0].message.content
#
#     except Exception as e:
#         print(f"Error in get_pr_review: {str(e)}")
#         return json.dumps({'status': 'error', 'message': str(e)})


import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from review.utils.prompts.cleanPrompt import GUIDELINE_PROMPT as CLEAN_PROMPT
# 환경 변수 로드
load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def file_code_review(code, pr_id=None):
    """
    파일 단위 코드 리뷰 함수.
    - code: 리뷰할 코드 내용.
    - pr_id: PR ID (Pull Request ID).
    """
    try:
        # 리뷰 모드 강제 설정
        review_mode = "clean mode"  # 무조건 clean mode로 설정
        print(f"Starting file_code_review with review_mode: {review_mode}")

        # 프롬프트 가져오기
        prompt = CLEAN_PROMPT.format(review=code)
        print(f"Generated file review prompt")

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt}],
            stream=False
        )

        # 응답 처리
        result = response.choices[0].message.content
        print(f"file Review Response:\n{result}")
        return result

    except Exception as e:
        print(f"Error in file_code_review: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})



# def file_code_review(code, pr_id=None):
#     """
#     파일 단위 코드 리뷰 함수.
#     - code: 리뷰할 코드 내용.
#     - pr_id: PR ID (Pull Request ID). Optional.
#     """
#     try:
#         review_mode = "clean mode"  # 기본값
#         if pr_id:
#             try:
#                 pr_review = PRReview.objects.get(id=pr_id)
#                 review_mode = pr_review.review_mode or "clean mode"
#             except PRReview.DoesNotExist:
#                 print(f"PR with ID {pr_id} not found. Using default 'clean mode'.")
#
#         # 모드에 따른 프롬프트 선택
#         if review_mode == "clean mode":
#             prompt = CLEAN_PROMPT.format(review=code)
#         elif review_mode == "optimize mode":
#             prompt = OPTIMIZE_PROMPT.format(review=code)
#         else:
#             raise ValueError(f"Invalid review mode: {review_mode}")
#
#         print(f"Generated prompt for mode '{review_mode}':\n{prompt}")
#
#         # OpenAI API 호출
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[{"role": "system", "content": prompt}],
#             stream=False,
#         )
#         result = response.choices[0].message.content
#         print(f"API Response:\n{result}")
#         return result
#
#     except Exception as e:
#         print(f"Error in file_code_review: {str(e)}")
#         return json.dumps({'status': 'error', 'message': str(e)})

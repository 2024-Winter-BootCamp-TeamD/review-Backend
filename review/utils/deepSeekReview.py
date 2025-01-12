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
        formatted_prompt = newbiePrompt.GUIDELINE_PROMPT.replace("{{user_question}}", code)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": formatted_prompt},
            ],
            stream=False
        )
        code_review = response.content
        print("code_review: ", response.choices[0].message.content)
        return code_review

    except Exception as e:
        print(f"Error in analyze_contract: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})

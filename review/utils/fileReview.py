import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from review.utils.prompts.filePrompts import (
    CLEAN_PROMPT, OPTIMIZE_PROMPT, BASIC_PROMPT, NEWBIE_PROMPT, STUDY_PROMPT
)

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def get_file_prompt(review_mode):
    prompts = {"clean": CLEAN_PROMPT,
               "optimize": OPTIMIZE_PROMPT,
               "basic": BASIC_PROMPT,
               "newbie": NEWBIE_PROMPT,
               "study": STUDY_PROMPT, }
    if review_mode not in prompts:
        raise ValueError(f"Invalid review_mode: {review_mode}. Valid modes are {list(prompts.keys())}.")
    return prompts[review_mode]

def file_code_review(review_mode, code):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": get_file_prompt(review_mode)},
                {"role": "user", "content": code}
            ],stream=False
        )
        code_review = response.choices[0].message.content
        print("code_review: ", code_review)
        return code_review

    except Exception as e:
        print(f"Error in analyze_contract: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})

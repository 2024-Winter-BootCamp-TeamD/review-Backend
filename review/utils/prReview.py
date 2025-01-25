import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from review.utils.prompts.prPrompts import (
    CLEAN_PROMPT, OPTIMIZE_PROMPT, BASIC_PROMPT, NEWBIE_PROMPT, STUDY_PROMPT
)

def get_pr_prompt(review_mode):
    prompts = {"clean": CLEAN_PROMPT,
               "optimize": OPTIMIZE_PROMPT,
               "basic": BASIC_PROMPT,
               "newbie": NEWBIE_PROMPT,
               "study": STUDY_PROMPT, }
    return prompts[review_mode]

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def get_pr_review(review, review_mode):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": get_pr_prompt(review_mode)},
                {"role": "user", "content": review}
            ], stream=False
        )
        pr_review = response.choices[0].message.content
        print("pr_review: ", response.choices[0].message.content)
        return pr_review

    except Exception as e:
        print(f"Error in making pr_review: {str(e)}")
        return json.dumps({'status': 'error', 'message': str(e)})

import os

import openai
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()

# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # 또는 "gpt-4"
    messages=[
        {"role": "user", "content": '''
        안녕 지피티
        '''}
    ]
)

print(response['choices'][0]['message']['content'])

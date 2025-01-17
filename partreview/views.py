from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
""""
<<<<<<< Updated upstream
from user.models import User
from django.http import StreamingHttpResponse
import time
import requests
from django.conf import settings
======"""
from .models import CodeReview
from user.models import User

class PartReviewView(APIView):
    def post(self, request):
        user_id = request.data.get("userId")
        code_snippet = request.data.get("code")

        if not user_id or not code_snippet:
            return Response({"error": "Missing userId or code snippet."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = User.objects.get(id=user_id)
            review_mode = user_profile.review_mode
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        def event_stream():
            try:
                yield f"codify: Review start. Mode: {review_mode}\n\n"
                time.sleep(1)

                review_result = call_deepseek_api(code_snippet, review_mode)
                yield f"codify: Review result: {review_result}\n\n"
                time.sleep(1)

                yield f"codify: Review completed.\n\n"

            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

def call_deepseek_api(code_snippet, review_mode):
    api_url = settings.DEEPSEEK_API_URL
    api_key = settings.DEEPSEEK_API_KEY

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"You are a code reviewer in {review_mode} mode. You must review in Korean."},
            {"role": "user", "content": code_snippet}
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        review_result = response.json()
        return review_result['choices'][0]['message']['content']
    else:
        error_msg = response.json().get("error", "Unknown error occurred.")
        raise Exception(f"DeepSeek API failed: {error_msg}")

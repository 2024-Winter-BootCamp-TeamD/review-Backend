from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from django.http import StreamingHttpResponse
import time
import requests
from django.conf import settings
from .models import CodeReview
from user.models import User

class PartReviewView(APIView):
    def post(self, request):
        # StreamingHttpResponse를 사용하여 스트리밍 응답 반환
        response = StreamingHttpResponse(self.event_stream(request), content_type="text/event-stream")
        response["Access-Control-Allow-Origin"] = "https://github.com"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def event_stream(self, request):
        try:
            # 요청 데이터에서 userId와 code snippet 추출
            user_id = request.data.get("userId")
            code_snippet = request.data.get("code")

            # 필수 데이터가 없는 경우 에러 반환
            if not user_id or not code_snippet:
                yield f"data: {{\"error\": \"Missing userId or code snippet.\"}}\n\n"
                return

            # 사용자 프로필 조회
            try:
                user_profile = User.objects.get(id=user_id)
                review_mode = user_profile.review_mode
            except User.DoesNotExist:
                yield f"data: {{\"error\": \"User not found.\"}}\n\n"
                return

            # 리뷰 시작 메시지 전송
            yield f"data: {{\"data\": \"Refactory: Review start. Mode: {review_mode}\"}}\n\n"
            time.sleep(1)

            # DeepSeek API 호출 및 스트리밍 응답 처리
            for chunk in self.call_deepseek_api(code_snippet, review_mode):
                yield chunk + "\n\n"

            # 리뷰 완료 메시지 전송
            yield f"data: {{\"message\": \"Refactory: Review completed.\"}}\n\n"

        except Exception as e:
            # 예외 발생 시 에러 메시지 전송
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    def call_deepseek_api(self, code_snippet, review_mode):
        api_url = settings.DEEPSEEK_API_URL
        api_key = settings.DEEPSEEK_API_KEY

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"당신은 '{review_mode}' 모드에서 코드를 검토하는 전문 리뷰어입니다. {review_mode} 모드의 코드 작성 지향 방향을 중점으로, 개선 사항과 권장 사항을 한국어로 상세히 작성하세요."},
                {"role": "user", "content": f"다음은 {review_mode} 모드로 검토해야 할 코드입니다. 이 코드는 특정 목적을 위해 작성되었으며, 개선점을 지적해주세요.\n\n{code_snippet}"}
            ],
            "stream": True
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        with requests.post(api_url, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                error_msg = response.json().get("error", "Unknown error occurred.")
                raise Exception(f"DeepSeek API failed: {error_msg}")

            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    decoded_chunk = chunk.decode("utf-8")
                    # data:로 시작하지 않으면 강제로 data:를 추가
                    if not decoded_chunk.startswith("data:"):
                        decoded_chunk = f"data: {decoded_chunk}"
                    yield f"{decoded_chunk}\n\n"

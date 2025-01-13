from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CodeReview
from user.models import User

class PartReviewView(APIView):
    def post(self, request):
        user_id = request.data.get("userId")
        code_snippet = request.data.get("code")

        if not user_id or not code_snippet:
            return Response({"error": "Wrong request"}, status=status.HTTP_400_BAD_REQUEST)

        # 유저 확인
        try:
            user_profile = User.objects.get(id=user_id)
            mode = user_profile.review_mode
        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        review = CodeReview.objects.create(user=user_profile.auth_user, code_snippet=code_snippet)  # auth_user 사용

        return Response(
            {
                "message": "Code review request received.",
                "mode": mode,
            },
            status=status.HTTP_200_OK,
        )
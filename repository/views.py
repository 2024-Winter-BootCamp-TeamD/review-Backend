from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Repository
from .serializers import RepositorySerializer


@api_view(['GET'])
def get_repositories(request):
    """
    /repositories?user_id=123  형태로 호출:
    - user_id가 없으면 400 반환
    - 있으면 해당 user_id에 해당하는 Repository 목록 반환
    """
    user_id = request.query_params.get('user_id', None)

    if not user_id:
        return Response(
            {"레포지토리 조회 실패"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # user_id가 정수인지 확인
    try:
        user_id = int(user_id)
    except ValueError:
        return Response(
            {"error_message": "user_id는 정수여야 합니다"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 해당 user_id를 가진 Repository들 조회
    repositories = Repository.objects.filter(user_id=user_id)
    serializer = RepositorySerializer(repositories, many=True)

    response_data = {"repositories": serializer.data}

    return Response(response_data, status=status.HTTP_200_OK)
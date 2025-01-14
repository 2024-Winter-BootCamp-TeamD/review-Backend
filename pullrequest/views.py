from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import PRReview
from .serializers import PRReviewSerializer

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = 'size'  # 페이지 크기 지정
    page_query_param = 'page'  # 페이지 번호 지정

class PRReviewListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        queryset = PRReview.objects.filter(is_deleted=False).select_related('user')

        # user 필터
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # 페이지네이션 적용
        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class PRReviewSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': '검색어를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.query_params.get('user')
        queryset = PRReview.objects.filter(title__icontains=query, is_deleted=False).select_related('user')

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # 검색 결과 없음 처리
        if not queryset.exists():
            return Response(
                {'message': '검색된 PR 리뷰가 없습니다.'},
                status=status.HTTP_200_OK
            )

        # 페이지네이션 적용
        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # 시리얼라이저 처리 및 응답 반환
        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
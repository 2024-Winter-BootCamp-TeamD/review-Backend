from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import PRReview
from .serializers import PRReviewSerializer

# 삭제된 유저, 리뷰 필터링 로직
def get_active_pr_reviews(user_id=None, query=None):
    queryset = PRReview.objects.filter(is_deleted=False, user__is_deleted=False)
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if query:
        queryset = queryset.filter(title__icontains=query)
    return queryset

# 페이지네이션
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = 'size'  # 페이지 크기 지정
    page_query_param = 'page'  # 페이지 번호 지정

# PR 리뷰 전체조회
class PRReviewListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        queryset = get_active_pr_reviews(user_id=user_id)

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

# PR 리뷰 검색
class PRReviewSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': '검색어를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.query_params.get('user')
        queryset = get_active_pr_reviews(user_id=user_id, query=query)

        if not queryset.exists():
            return Response(
                {'message': '검색된 PR 리뷰가 없습니다.'},
                status=status.HTTP_200_OK
            )

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

# 최신 7개 PR 평균 등급 조회
class PRReviewAverageGradeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return Response(
                {"error_message": "사용자를 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = get_active_pr_reviews(user_id=user_id).order_by('-id')[:7]

        if not queryset.exists():
            return Response(
                {"error_message": "해당 사용자의 PR 리뷰가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        serialized_data = [
            {
                "pull_request_id": pr.id,
                "title": pr.title,
                "aver_grade": pr.aver_grade,
                "created_at": pr.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for pr in queryset
        ]

        return Response({"data": serialized_data}, status=status.HTTP_200_OK)

# 최신 10개 문제 유형 조회
class PRReviewTroubleTypeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return Response(
                {"error_message": "사용자를 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = get_active_pr_reviews(user_id=user_id).exclude(problem_type__isnull=True).order_by('-id')[:10]

        if not queryset.exists():
            return Response(
                {"error_message": "해당 사용자의 PR 리뷰가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )

        problem_types = queryset.values_list('problem_type', flat=True)
        problem_type_count = Counter(problem_types)

        return Response({"data": problem_type_count}, status=status.HTTP_200_OK)

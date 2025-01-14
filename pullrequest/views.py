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

# 중복된 쿼리셋 검사
def get_valid_queryset(queryset, empty_message):
    if not queryset.exists():
        raise ValueError(empty_message)
    return queryset

# 성공 응답 처리
def success_response(data, status_code=status.HTTP_200_OK):
    return Response(data, status=status_code)

# 에러 응답 처리
def error_response(message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    response_data = {"error_message": message}
    if details:
        response_data["details"] = details
    return Response(response_data, status=status_code)

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

        if not queryset.exists():
            return error_response("PR 리뷰가 없습니다.", status_code=status.HTTP_404_NOT_FOUND)

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

# PR 리뷰 검색
class PRReviewSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return error_response("검색어를 입력해주세요.", status_code=status.HTTP_400_BAD_REQUEST)

        user_id = request.query_params.get('user')
        queryset = get_active_pr_reviews(user_id=user_id, query=query)

        if not queryset.exists():
            return success_response({"message": "검색된 PR 리뷰가 없습니다."})

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = PRReviewSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

# 최신 7개 PR 평균 등급 조회
class PRReviewAverageGradeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return error_response("사용자를 입력하세요.")

        try:
            queryset = get_valid_queryset(
                get_active_pr_reviews(user_id=user_id).order_by('-id')[:7],
                "해당 사용자의 PR 리뷰가 없습니다."
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

            return success_response({"data": serialized_data})

        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)

# 최신 10개 문제 유형 조회
class PRReviewTroubleTypeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return error_response("사용자를 입력하세요.")

        try:
            queryset = get_valid_queryset(
                get_active_pr_reviews(user_id=user_id).exclude(problem_type__isnull=True).order_by('-id')[:10],
                "해당 사용자의 PR 리뷰가 없습니다."
            )

            problem_types = queryset.values_list('problem_type', flat=True)
            problem_type_count = Counter(problem_types)

            return success_response({"data": problem_type_count})

        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)

# 전체 PR 모드 카테고리 통계 조회
class PRReviewCategoryStatisticsView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        if not user_id:
            return error_response("사용자를 입력하세요.")

        try:
            queryset = get_valid_queryset(
                get_active_pr_reviews(user_id=user_id),
                "해당 사용자의 PR 리뷰가 없습니다."
            )

            review_modes = queryset.values_list('review_mode', flat=True)
            mode_statistics = Counter(review_modes)

            return success_response({"statistics": mode_statistics})

        except ValueError as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
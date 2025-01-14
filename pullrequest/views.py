from collections import Counter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import PRReview
from .serializers import PRReviewSerializer

# 삭제된 유저, 리뷰 필터링 로직
def get_active_pr_reviews(user_id=None, query=None):
    # user__is_deleted 검사하는 부분은 필요 없어 보이지만 보안을 위해 넣어둠
    queryset = PRReview.objects.filter(is_deleted=False, user__is_deleted=False)
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if query:
        queryset = queryset.filter(title__icontains=query)
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
    page_size_query_param = 'size'  # 클라이언트가 페이지 크기 조정 가능
    page_query_param = 'page'  # 페이지 번호
    max_page_size = 100  # 최대 페이지 크기 제한

    def get_paginated_response(self, data):
        return Response({
            "currentPage": self.page.number,
            "totalPages": self.page.paginator.num_pages,
            "totalItems": self.page.paginator.count,
            "hasNextPage": self.page.has_next(),
            "data": data
        })

# PR 리뷰 전체조회
class PRReviewListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user') # request.user.id 사용??
        queryset = get_active_pr_reviews(user_id=user_id)

        if not queryset.exists():
            return success_response({"data": {}})
            # return error_response("PR 리뷰가 없습니다.", status_code=status.HTTP_404_NOT_FOUND)

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PRReviewSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

# PR 리뷰 검색
class PRReviewSearchView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        title = request.query_params.get('title', '').strip()
        queryset = get_active_pr_reviews(user_id=user_id, query=title)

        if not queryset.exists():
            return success_response({"data": {}})

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PRReviewSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

# 최신 7개 PR 평균 등급 조회
class PRReviewAverageGradeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        queryset = get_active_pr_reviews(user_id=user_id).order_by('-id')[:7]

        # 빈 배열로 반환?
        if not queryset.exists():
            return success_response({"data": {}})
            # return error_response("PR 리뷰가 존재하지 않습니다.", status_code=status.HTTP_404_NOT_FOUND)

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

# 최신 10개 문제 유형 조회
class PRReviewTroubleTypeView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        # 문제 유형이 null이 아닌 경우만 가져옴
        queryset = get_active_pr_reviews(user_id=user_id).exclude(problem_type__isnull=True).order_by('-id')[:10]

        if not queryset.exists():
            return success_response({"data": {}})

        problem_types = queryset.values_list('problem_type', flat=True)
        problem_type_count = Counter(problem_types)

        return success_response({"data": problem_type_count})

# 전체 PR 모드 카테고리 통계 조회
class PRReviewCategoryStatisticsView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user')
        queryset = get_active_pr_reviews(user_id=user_id)

        if not queryset.exists():
            return success_response({"data": {}})

        review_modes = queryset.values_list('review_mode', flat=True)
        mode_statistics = Counter(review_modes)

        return success_response({"statistics": mode_statistics})

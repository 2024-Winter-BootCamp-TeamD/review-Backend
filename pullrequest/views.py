from collections import Counter

from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import PRReview
from .serializers import PRReviewSerializer

# 필수 필터링 로직
def filter_pr_reviews(user_id):
    return PRReview.objects.filter(is_deleted=False, user_id=user_id)

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
    page_size_query_param = 'size'  # 요청
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

# 직렬화 반환
def get_serialized_response(queryset, request, serializer_class):
    paginator = CustomPageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)

# PR 리뷰 전체조회
class PRReviewListView(APIView):
    def get(self, request):
        queryset = filter_pr_reviews(request.query_params.get('user_id')) # request.user.id 사용??
        if not queryset:
            return success_response({"data": {}})

        return get_serialized_response(queryset, request, PRReviewSerializer)

# PR 리뷰 검색
class PRReviewSearchView(APIView):
    def get(self, request):
        title = request.query_params.get('title', '').strip()
        if not title:
            return error_response("검색어를 입력해주세요.", status_code=status.HTTP_400_BAD_REQUEST)

        queryset = filter_pr_reviews(request.query_params.get('user_id')).filter(title__icontains=title)
        if not queryset:
            return success_response({"data": {}})

        return get_serialized_response(queryset, request, PRReviewSerializer)

# 최신 7개 PR 평균 등급 조회
class PRReviewAverageGradeView(APIView):
    def get(self, request):
        queryset = filter_pr_reviews(request.query_params.get('user_id')).order_by('-id')[:7]
        if not queryset:
            return success_response({"data": {}})

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
        queryset = filter_pr_reviews(request.query_params.get('user_id')).exclude(problem_type__isnull=True).order_by('-id')[:10]
        if not queryset:
            return success_response({"data": {}})

        problem_types = queryset.values_list('problem_type', flat=True)
        problem_type_count = Counter(problem_types)

        return success_response({"data": problem_type_count})

# 전체 PR 모드 카테고리 통계 조회
class PRReviewCategoryStatisticsView(APIView):
    def get(self, request):
        queryset = filter_pr_reviews(request.query_params.get('user_id'))
        if not queryset:
            return success_response({"statistics": {}})

        review_mode_count = queryset.values('review_mode').annotate(count=Count('review_mode')).order_by('-count')

        return success_response({"statistics": {item['review_mode']: item['count'] for item in review_mode_count}})

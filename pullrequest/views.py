from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PRReview
from .serializers import PRReviewSerializer

class PRReviewListView(APIView):
    def get(self, request):
        reviews = PRReview.objects.filter(is_deleted=False).select_related('user')
        serializer = PRReviewSerializer(reviews, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

class PRReviewSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()  # 검색어 가져오기
        if not query:
            return Response({'error': '검색어를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        reviews = PRReview.objects.filter(title__icontains=query, is_deleted=False).select_related('user')

        if not reviews.exists():
            return Response({'message': '검색된 PR 리뷰가 없습니다.'}, status=status.HTTP_200_OK)

        serializer = PRReviewSerializer(reviews, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
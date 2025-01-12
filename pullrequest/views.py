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
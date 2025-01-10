from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PRReview
from .serializers import PRReviewSerializer

class PRReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviews = PRReview.objects.filter(is_deleted=False)
        serializer = PRReviewSerializer(reviews, many=True)
        return Response(serializer.data)

from rest_framework import serializers
from .models import PRReview

class PRReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PRReview
        fields = [
            'id', 'user', 'title', 'pr_url', 'aver_grade',
            'problem_type', 'review_mode', 'total_review',
            'is_deleted', 'created_at', 'updated_at'
        ]


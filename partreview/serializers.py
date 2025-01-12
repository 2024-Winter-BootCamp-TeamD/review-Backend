from rest_framework import serializers
from .models import CodeReview


class CodeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeReview
        fields = ['id', 'user', 'code_snippet', 'created_at']

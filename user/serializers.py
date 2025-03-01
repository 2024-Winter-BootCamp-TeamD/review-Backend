from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['github_id', 'user_details', 'github_username', 'email',
                  'profile_image', 'review_mode', 'created_at', 'updated_at']

    @staticmethod
    def get_user_details(obj):
        # auth_user가 테이블에 없으므로 None 반환
        return {
            "id": obj.id or "Unknown",
            "github_username": obj.github_username or "No username",
        }

    def validate_review_mode(self, value):
        valid_modes = [choice[0] for choice in User.REVIEW_MODES]
        if value not in valid_modes:
            raise serializers.ValidationError(
                f"Invalid review mode. Choose one of: {', '.join(valid_modes)}"
            )
        return value

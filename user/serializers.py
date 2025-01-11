from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['github_id', 'user_details', 'github_username', 'email',
                  'profile_image', 'review_mode', 'created_at', 'updated_at',]

    @staticmethod
    def get_user_details(obj):
        return {
            "id": obj.user.id,
        }
    def validate_review_mode(self, value):
        valid_modes = [choice[0] for choice in UserProfile.REVIEW_MODES]
        if value not in valid_modes:
            raise serializers.ValidationError(f"Invalid review mode. Choose one of: {', '.join(valid_modes)}")
        return value
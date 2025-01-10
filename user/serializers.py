from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'github_id', 'user_details', 'github_username', 'email',
                  'profile_image', 'created_at', 'updated_at']

    @staticmethod
    def get_user_details(obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }

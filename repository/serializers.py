from rest_framework import serializers
from .models import Repository

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'user_id', 'organization', 'name', 'repository_image', 'is_apply',
                  'language', 'description', 'visibility', 'repo_updated_at']

from django.db import models

from user.models import User


# Create your models here.
class Repository(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    repository_github_id = models.CharField(max_length=20, unique=True)
    is_apply = models.BooleanField(default=False)
    organization = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100)
    repository_image = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 기본값 제거
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

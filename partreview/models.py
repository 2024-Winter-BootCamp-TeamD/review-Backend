from django.db import models
from django.contrib.auth.models import User


class CodeReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # GitHub
    code_snippet = models.TextField()  # 드래그된 코드 가져오기
    created_at = models.DateTimeField(auto_now_add=True)  # 시간

    def __str__(self):
        return f"Review by {self.user.username} at {self.created_at}"

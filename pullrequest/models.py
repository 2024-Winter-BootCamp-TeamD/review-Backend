from django.db import models

from user.models import User


class PRReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100) #####
    pr_url = models.URLField(max_length=255)
    aver_grade = models.CharField(max_length=20)
    problem_type = models.CharField(max_length=20, null=True, blank=True)
    review_mode = models.CharField(max_length=20)
    total_review = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FileReview(models.Model):
    id = models.AutoField(primary_key=True)
    pr_review = models.ForeignKey(PRReview, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    comment = models.TextField()
    grade = models.CharField(max_length=20)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # 기본값 제거
    updated_at = models.DateTimeField(auto_now=True)

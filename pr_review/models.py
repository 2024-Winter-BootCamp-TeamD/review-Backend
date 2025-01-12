from django.db import models

from user.models import User


# Create your models here.
class PrReview(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    title = models.CharField(max_length=100, null=True)
    pr_url = models.CharField(max_length=255)
    aver_grade = models.CharField(max_length=20)
    problem_type = models.CharField(max_length=20)
    total_review = models.TextField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class FileReview(models.Model):
    id = models.AutoField(primary_key=True)
    pr_review_id = models.ForeignKey(PrReview, on_delete=models.CASCADE, db_column='pr_review_id')
    file_path = models.CharField(max_length=255)
    comment = models.TextField
    grade = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
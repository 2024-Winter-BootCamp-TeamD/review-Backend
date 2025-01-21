from django.db import models

class User(models.Model):
    REVIEW_MODES = [
        ('basic mode', 'Basic Mode'),
        ('clean mode', 'Clean Mode'),
        ('optimize mode', 'Optimize Mode'),
        ('new bie mode', 'New Bie Mode'),
        ('study mode', 'Study Mode')
    ]
    id = models.AutoField(primary_key=True)
    github_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    profile_image = models.URLField(max_length=200, blank=True, null=True)
    github_username = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    review_mode = models.CharField(max_length=20, choices=REVIEW_MODES, default='clean')
    created_at = models.DateTimeField(auto_now_add=True)  # 기본값 제거
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_user'
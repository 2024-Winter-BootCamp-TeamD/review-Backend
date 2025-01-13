# Generated by Django 5.1.4 on 2025-01-13 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0002_alter_user_review_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='PRReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('pr_url', models.URLField(max_length=255)),
                ('aver_grade', models.CharField(max_length=20)),
                ('problem_type', models.CharField(blank=True, max_length=20, null=True)),
                ('review_mode', models.CharField(max_length=20)),
                ('al_review', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
        migrations.CreateModel(
            name='FileReview',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file_path', models.CharField(max_length=255)),
                ('comment', models.TextField()),
                ('grade', models.CharField(max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pr_review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pullrequest.prreview')),
            ],
        ),
    ]

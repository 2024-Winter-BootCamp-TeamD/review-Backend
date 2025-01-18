# Generated by Django 5.1.4 on 2025-01-18 18:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repository_github_id', models.CharField(max_length=20, unique=True)),
                ('is_apply', models.BooleanField(default=False)),
                ('hook_id', models.IntegerField(blank=True, null=True)),
                ('organization', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=100)),
                ('repository_image', models.URLField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.CharField(blank=True, db_collation='utf8mb4_unicode_ci', max_length=255, null=True)),
                ('visibility', models.CharField(max_length=20)),
                ('repo_updated_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]

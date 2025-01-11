# Generated by Django 5.1.4 on 2025-01-11 10:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('github_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('profile_image', models.URLField(blank=True, null=True)),
                ('github_username', models.CharField(max_length=100)),
                ('access_token', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('review_mode', models.CharField(choices=[('basic mode', 'Basic Mode'), ('clean mode', 'Clean Mode'), ('optimize mode', 'Optimize Mode'), ('new bie mode', 'New Bie Mode'), ('study mode', 'Study Mode')], default='Basic Mode', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('github_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('profile_image', models.URLField(blank=True, null=True)),
                ('github_username', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('review_mode', models.CharField(choices=[('basic mode', 'Basic Mode'), ('clean mode', 'Clean Mode'), ('optimize mode', 'Optimize Mode'), ('new bie mode', 'New Bie Mode'), ('study mode', 'Study Mode')], default='Basic Mode', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

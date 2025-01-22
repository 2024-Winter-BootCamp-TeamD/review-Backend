# Generated by Django 5.1.5 on 2025-01-22 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                ('review_mode', models.CharField(choices=[('basic mode', 'Basic Mode'), ('clean mode', 'Clean Mode'), ('optimize mode', 'Optimize Mode'), ('new bie mode', 'New Bie Mode'), ('study mode', 'Study Mode')], default='basic mode', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_user',
            },
        ),
    ]

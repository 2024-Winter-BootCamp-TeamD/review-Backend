# Generated by Django 5.1.4 on 2025-01-09 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_userprofile_created_at_userprofile_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='github_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]

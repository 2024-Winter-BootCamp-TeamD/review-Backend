# Generated by Django 5.1.5 on 2025-01-22 06:04


import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pullrequest', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('report_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('pdf_url', models.CharField(max_length=255)),
                ('review_num', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'db_table': 'report_report',
            },
        ),
        migrations.CreateModel(
            name='ReportPrReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('pr_review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_reviews', to='pullrequest.prreview')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pr_reviews', to='report.report')),
            ],
            options={
                'db_table': 'report_prreview',
                'unique_together': {('report', 'pr_review')},
            },
        ),
    ]

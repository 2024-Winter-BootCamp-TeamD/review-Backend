import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('repository_github_id', models.CharField(max_length=20, unique=True)),
                ('is_apply', models.BooleanField(default=False)),
                ('hook_id', models.IntegerField(null=True)),
                ('organization', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=100)),
                ('repository_image', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]

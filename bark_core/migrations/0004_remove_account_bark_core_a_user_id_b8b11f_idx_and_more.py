# Generated by Django 5.1.1 on 2024-09-29 01:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bark_core', '0003_account_profile_picture_delete_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='account',
            name='bark_core_a_user_id_b8b11f_idx',
        ),
        migrations.RemoveField(
            model_name='account',
            name='account_number',
        ),
        migrations.AddField(
            model_name='account',
            name='account_number_hashed',
            field=models.CharField(default=0, max_length=64, unique=True),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='account',
            index=models.Index(fields=['user', 'account_number_hashed'], name='bark_core_a_user_id_05d64b_idx'),
        ),
    ]

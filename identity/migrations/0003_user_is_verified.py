# Generated by Django 5.0.3 on 2024-03-07 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0002_rename_admin_user_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.0.3 on 2024-03-07 13:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identity', '0003_user_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.IntegerField(blank=True, null=True)),
                ('otp_expiry', models.DateTimeField(blank=True, null=True)),
                ('otp_type', models.CharField(blank=True, choices=[('Password', 'Password'), ('Login', 'Login')], default='Login', max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_otp', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

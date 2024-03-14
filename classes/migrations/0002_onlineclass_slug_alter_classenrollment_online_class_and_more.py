# Generated by Django 5.0.3 on 2024-03-11 10:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineclass',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='classenrollment',
            name='online_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classes.onlineclass'),
        ),
        migrations.AlterField(
            model_name='onlineclass',
            name='attendees',
            field=models.ManyToManyField(related_name='enrolled_classes', through='classes.ClassEnrollment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='onlineclass',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
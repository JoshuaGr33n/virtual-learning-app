# Generated by Django 5.0.3 on 2024-03-11 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0008_classenrollment_enrollment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlineclass',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

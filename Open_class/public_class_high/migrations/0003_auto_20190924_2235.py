# Generated by Django 2.2.3 on 2019-09-24 14:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_class_high', '0002_auto_20190924_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attend_data',
            name='attend_people',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='參加的人'),
        ),
    ]

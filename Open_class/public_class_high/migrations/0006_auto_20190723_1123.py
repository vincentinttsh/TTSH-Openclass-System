# Generated by Django 2.2.3 on 2019-07-23 03:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public_class_high', '0005_auto_20190723_1035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attend_data',
            options={'verbose_name': '高中公開觀課報名人數', 'verbose_name_plural': '高中公開觀課報名人數'},
        ),
        migrations.AlterField(
            model_name='high_class',
            name='attend_data',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='public_class_high.Attend_data', verbose_name='參加資料'),
        ),
    ]

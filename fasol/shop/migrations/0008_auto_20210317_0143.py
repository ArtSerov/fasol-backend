# Generated by Django 3.1.7 on 2021-03-16 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20210317_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='representation',
            field=models.ImageField(blank=True, null=True, upload_to='сategory/', verbose_name='Изображение'),
        ),
    ]

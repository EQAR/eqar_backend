# Generated by Django 2.0.8 on 2019-01-31 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0008_auto_20180605_0915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programme',
            options={'ordering': ['id', 'report']},
        ),
    ]

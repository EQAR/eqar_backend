# Generated by Django 2.2.28 on 2023-08-22 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0017_auto_20230813_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='field_study_title',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='programmelearningoutcome',
            name='learning_outcome_esco_title',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
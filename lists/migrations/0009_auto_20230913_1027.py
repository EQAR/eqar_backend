# Generated by Django 2.2.28 on 2023-09-13 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0008_delete_identifiersource'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='identifierresource',
            name='id',
        ),
        migrations.AddField(
            model_name='identifierresource',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='identifierresource',
            name='source',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='identifierresource',
            name='title',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='identifierresource',
            name='resource',
            field=models.CharField(max_length=150, primary_key=True, serialize=False),
        ),
    ]

# Generated by Django 2.2.28 on 2023-09-11 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0032_remove_institutionidentifier_source'),
        ('lists', '0007_identifiersource'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IdentifierSource',
        ),
    ]

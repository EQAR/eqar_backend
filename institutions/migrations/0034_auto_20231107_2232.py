# Generated by Django 2.2.28 on 2023-11-07 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0033_migrate_institution_identifiers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutionidentifier',
            name='agency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agencies.Agency'),
        ),
        migrations.AlterField(
            model_name='institutionidentifier',
            name='resource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='lists.IdentifierResource'),
        ),
    ]

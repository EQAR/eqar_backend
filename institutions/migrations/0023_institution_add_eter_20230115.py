# Generated by Django 2.2.28 on 2023-01-15 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0022_auto_20210922_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='eter_identifier',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddIndex(
            model_name='institution',
            index=models.Index(fields=['eter_identifier'], name='deqar_insti_eter_id_0ebb8f_idx'),
        ),
    ]

# Generated by Django 2.2.13 on 2020-07-17 17:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institutions', '0019_auto_20200616_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='institutions_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]

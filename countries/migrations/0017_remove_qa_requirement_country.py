from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Requirements are linked to their country through their group only.
    """

    dependencies = [
        ('countries', '0016_migrate_legacy_qa_requirements'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countryqarequirement',
            name='country',
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirements', to='countries.countryqarequirementgroup'),
        ),
    ]

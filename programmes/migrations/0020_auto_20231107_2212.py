from django.db import migrations


def create_degree_outcomes(apps, schema_editor):
    DegreeOutcome = apps.get_model("lists", "DegreeOutcome")
    DegreeOutcome.objects.get_or_create(
        id=1, outcome='Full degree'
    )
    DegreeOutcome.objects.get_or_create(
        id=2, outcome='No full degree'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0019_auto_20230831_1109'),
    ]

    operations = [
        migrations.RunPython(create_degree_outcomes),
    ]

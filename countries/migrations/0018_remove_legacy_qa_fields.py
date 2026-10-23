from django.db import migrations


class Migration(migrations.Migration):
    """
    Drops legacy QA information that has been transferred into QA requirements groups by 0016.
    """

    dependencies = [
        ('countries', '0017_remove_qa_requirement_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='conditions',
        ),
        migrations.RemoveField(
            model_name='country',
            name='eligibility',
        ),
        migrations.RemoveField(
            model_name='country',
            name='european_approach_note',
        ),
        migrations.RemoveField(
            model_name='country',
            name='external_QAA_note',
        ),
        migrations.RemoveField(
            model_name='country',
            name='recognition',
        ),
        migrations.RemoveField(
            model_name='countryqarequirement',
            name='qa_requirement',
        ),
        migrations.RemoveField(
            model_name='countryqarequirement',
            name='qa_requirement_type',
        ),
        migrations.DeleteModel(
            name='CountryQARequirementType',
        ),
    ]

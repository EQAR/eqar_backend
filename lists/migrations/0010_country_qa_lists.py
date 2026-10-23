from pathlib import Path

import yaml
from django.db import migrations, models


FIXTURE = Path(__file__).resolve().parent.parent / 'fixtures' / 'country_qa_lists.yaml'


def seed_lists(apps, schema_editor):
    """
    Seeds the lists from the fixture, using historical models: loaddata would use the current models, which
    breaks this migration on new databases once the models change.
    """
    with FIXTURE.open() as f:
        entries = yaml.safe_load(f)
    for entry in entries:
        model = apps.get_model(entry['model'])
        field_names = {field.name for field in model._meta.concrete_fields}
        defaults = {name: value for name, value in entry['fields'].items() if name in field_names}
        model.objects.update_or_create(pk=entry['pk'], defaults=defaults)


def controlled_list_fields():
    return [
        ('id', models.AutoField(primary_key=True, serialize=False)),
        ('title', models.CharField(max_length=255)),
        ('uri', models.URLField(blank=True, max_length=255, null=True)),
        ('description', models.TextField(blank=True)),
    ]


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0009_auto_20230913_1027'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrossBorderPossibility',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Cross-border QA Possibility',
                'verbose_name_plural': 'Cross-border QA Possibilities',
                'db_table': 'deqar_list_cross_border_possibilities',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CrossBorderApproval',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Cross-border QA Approval',
                'verbose_name_plural': 'Cross-border QA Approvals',
                'db_table': 'deqar_list_cross_border_approvals',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CrossBorderRequirement',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Cross-border QA Requirement',
                'verbose_name_plural': 'Cross-border QA Requirements',
                'db_table': 'deqar_list_cross_border_requirements',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CrossBorderCriteria',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Cross-border QA Criteria',
                'verbose_name_plural': 'Cross-border QA Criteria',
                'db_table': 'deqar_list_cross_border_criteria',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CrossBorderDecision',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Cross-border QA Decision',
                'verbose_name_plural': 'Cross-border QA Decisions',
                'db_table': 'deqar_list_cross_border_decisions',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EuropeanApproachPossibility',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'European Approach Possibility',
                'verbose_name_plural': 'European Approach Possibilities',
                'db_table': 'deqar_list_european_approach_possibilities',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TnePossible',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE Possibility',
                'verbose_name_plural': 'TNE Possibilities',
                'db_table': 'deqar_list_tne_possible',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TneApprovalOutgoing',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE Approval (outgoing)',
                'verbose_name_plural': 'TNE Approvals (outgoing)',
                'db_table': 'deqar_list_tne_approvals_outgoing',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TneQaOutgoing',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE QA Regime (outgoing)',
                'verbose_name_plural': 'TNE QA Regimes (outgoing)',
                'db_table': 'deqar_list_tne_qa_outgoing',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TneOriginGroup',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE Origin Country Group',
                'verbose_name_plural': 'TNE Origin Country Groups',
                'db_table': 'deqar_list_tne_origin_groups',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TneApprovalIncoming',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE Approval (incoming)',
                'verbose_name_plural': 'TNE Approvals (incoming)',
                'db_table': 'deqar_list_tne_approvals_incoming',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TneQaIncoming',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'TNE QA Regime (incoming)',
                'verbose_name_plural': 'TNE QA Regimes (incoming)',
                'db_table': 'deqar_list_tne_qa_incoming',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='McQa',
            fields=controlled_list_fields(),
            options={
                'verbose_name': 'Micro-credential QA Regime',
                'verbose_name_plural': 'Micro-credential QA Regimes',
                'db_table': 'deqar_list_mc_qa',
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.RunPython(seed_lists, migrations.RunPython.noop),
    ]

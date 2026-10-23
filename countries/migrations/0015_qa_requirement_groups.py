import datetime

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    New structure for QA requirements (grouped by institution types), incoming TNE regulations and QF/LRC dates.

    Requirements temporarily keep their country link; they are assigned to groups in 0016 and the country link is
    dropped in 0017.
    """

    dependencies = [
        ('agencies', '0019_alter_agencyactivitygroup_options'),
        ('lists', '0010_country_qa_lists'),
        ('countries', '0014_delete_countryhistorical'),
    ]

    operations = [
        # country dates
        migrations.AddField(
            model_name='country',
            name='lrc_signatory_date',
            field=models.DateField(blank=True, help_text='when the country signed the Lisbon Recognition Convention; empty if it has not signed', null=True, verbose_name='LRC signatory date'),
        ),
        migrations.AddField(
            model_name='country',
            name='qf_ehea_alignment_date',
            field=models.DateField(blank=True, help_text='when the country self-certified its NQF against the QF-EHEA; empty if it has not', null=True, verbose_name='QF-EHEA alignment date'),
        ),
        migrations.AddField(
            model_name='country',
            name='eqf_alignment_date',
            field=models.DateField(blank=True, help_text='when the country referenced its NQF against the EQF; empty if it has not', null=True, verbose_name='EQF alignment date'),
        ),

        # QA requirements groups
        migrations.CreateModel(
            name='CountryQARequirementGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('combination_logic', models.CharField(choices=[('AND', 'cumulative (AND)'), ('OR', 'alternative (OR)')], default='AND', help_text='whether the requirements in this group are cumulative or alternative', max_length=3)),
                ('outgoing_tne_conditions', models.TextField(blank=True, verbose_name='outgoing TNE conditions')),
                ('mc_possible', models.BooleanField(default=False, help_text='HEIs in this group can award micro-credentials that are linked to the QF-EHEA or bear ECTS credits', verbose_name='MC possible')),
                ('mc_credit_limit', models.PositiveSmallIntegerField(blank=True, help_text='upper limit of ECTS for a micro-credential', null=True, verbose_name='MC credit limit')),
                ('mc_qa_note', models.TextField(blank=True, verbose_name='MC QA notes')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qa_requirement_groups', to='countries.country')),
                ('institution_types', models.ManyToManyField(blank=True, related_name='qa_requirement_groups', to='countries.countryinstitutiontype')),
                ('mc_qa', models.ManyToManyField(blank=True, related_name='+', to='lists.mcqa', verbose_name='MC QA regime')),
                ('outgoing_tne_approval', models.ManyToManyField(blank=True, related_name='+', to='lists.tneapprovaloutgoing', verbose_name='outgoing TNE approval needed')),
                ('outgoing_tne_possible', models.ForeignKey(blank=True, help_text='whether HEIs can offer TNE in other systems', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.tnepossible', verbose_name='outgoing TNE possible')),
                ('outgoing_tne_qa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.tneqaoutgoing', verbose_name='outgoing TNE QA regime')),
            ],
            options={
                'verbose_name': 'Country QA Requirements Group',
                'db_table': 'deqar_country_qa_requirement_groups',
                'ordering': ('id',),
            },
        ),

        # QA requirements: new structure, legacy fields become optional
        migrations.AlterModelOptions(
            name='countryqarequirement',
            options={'ordering': ('id',), 'verbose_name': 'Country QA Requirement'},
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.country'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requirements', to='countries.countryqarequirementgroup'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='activity_group',
            field=models.ForeignKey(blank=True, help_text='the type of QA review that needs to be passed to satisfy this requirement', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='country_qa_requirements', to='agencies.agencyactivitygroup', verbose_name='ESG activity group'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='duration',
            field=models.PositiveSmallIntegerField(blank=True, help_text='validity or length of accreditation cycles, in months', null=True),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='initial_only',
            field=models.BooleanField(default=False, help_text='requirement only applies to new institutions/programmes initially, rather than cyclically'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='fields_of_education',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=70), blank=True, default=list, help_text='ISCED-F codes or URIs, separated by commas; empty if the requirement applies to all fields', size=None),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='qf_ehea_levels',
            field=models.ManyToManyField(blank=True, help_text='empty if the requirement applies to all levels', related_name='+', to='lists.qfehealevel', verbose_name='QF-EHEA levels'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='full_degrees',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='micro_credentials',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_possible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.crossborderpossibility', verbose_name='CBQA possible'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_approval',
            field=models.ManyToManyField(blank=True, related_name='+', to='lists.crossborderapproval', verbose_name='CBQA approval needed'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_requirements',
            field=models.ManyToManyField(blank=True, related_name='+', to='lists.crossborderrequirement', verbose_name='CBQA requirements'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_other_requirements_note',
            field=models.TextField(blank=True, verbose_name='CBQA other requirements note'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_criteria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.crossbordercriteria', verbose_name='CBQA criteria'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='cbqa_recognition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.crossborderdecision', verbose_name='CBQA recognition'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='ea_possible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.europeanapproachpossibility', verbose_name='EA possible'),
        ),
        migrations.AddField(
            model_name='countryqarequirement',
            name='ea_note',
            field=models.TextField(blank=True, verbose_name='EA note'),
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='qa_requirement',
            field=models.CharField(blank=True, max_length=500, verbose_name='legacy title'),
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='qa_requirement_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.countryqarequirementtype', verbose_name='legacy type'),
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='qa_requirement_note',
            field=models.TextField(blank=True, verbose_name='notes'),
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='requirement_valid_from',
            field=models.DateField(default=datetime.date.today, verbose_name='valid from'),
        ),
        migrations.AlterField(
            model_name='countryqarequirement',
            name='requirement_valid_to',
            field=models.DateField(blank=True, null=True, verbose_name='valid to'),
        ),

        # regulations can be linked to a group
        migrations.AlterModelOptions(
            name='countryqaaregulation',
            options={'verbose_name': 'Country QAA Regulation'},
        ),
        migrations.AddField(
            model_name='countryqaaregulation',
            name='group',
            field=models.ForeignKey(blank=True, help_text='QA requirements group the regulation applies to; empty for general links', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='regulations', to='countries.countryqarequirementgroup'),
        ),

        # incoming TNE
        migrations.CreateModel(
            name='CountryIncomingTneRegulation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('incoming_tne_conditions', models.TextField(blank=True, verbose_name='incoming TNE conditions')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_tne_regulations', to='countries.country')),
                ('incoming_tne_approval', models.ManyToManyField(blank=True, related_name='+', to='lists.tneapprovalincoming', verbose_name='incoming TNE approval needed')),
                ('incoming_tne_possible', models.ForeignKey(help_text='whether foreign HEIs can offer TNE in the country', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.tnepossible', verbose_name='incoming TNE possible')),
                ('incoming_tne_qa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='lists.tneqaincoming', verbose_name='incoming TNE QA regime')),
                ('origin_groups', models.ManyToManyField(blank=True, related_name='+', to='lists.tneorigingroup', verbose_name='origin country groups')),
            ],
            options={
                'verbose_name': 'Country Incoming TNE Regulation',
                'db_table': 'deqar_country_incoming_tne_regulations',
                'ordering': ('id',),
            },
        ),
    ]

# Generated by Django 2.2.28 on 2023-08-07 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0004_assessment_degreeoutcome_ectscredit'),
        ('programmes', '0012_auto_20190509_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='assessment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lists.Assessment'),
        ),
        migrations.AddField(
            model_name='programme',
            name='degree_outcome',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='lists.DegreeOutcome'),
        ),
        migrations.AddField(
            model_name='programme',
            name='ects_credit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lists.ECTSCredit'),
        ),
        migrations.AddField(
            model_name='programme',
            name='isced',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AddField(
            model_name='programme',
            name='mc_as_part_of_accreditation',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ProgrammeLearningOutcome',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('learning_outcome', models.CharField(blank=True, max_length=70, null=True)),
                ('learning_outcome_description', models.TextField(blank=True, null=True)),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='programmes.Programme')),
            ],
            options={
                'verbose_name': 'Programme Learning Outcome',
                'db_table': 'deqar_programme_learning_outcomes',
                'unique_together': {('programme', 'learning_outcome')},
            },
        ),
    ]

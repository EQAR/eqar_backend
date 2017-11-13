from django.db import models


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    alpha2 = models.CharField(max_length=2, blank=True)
    alpha3 = models.CharField(max_length=3)
    country_name_en = models.CharField(unique=True, max_length=100)
    qa_requirement_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'list_countries'


class CountryQARequirement(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.PROTECT)
    qa_requirement = models.CharField(max_length=200, blank=True)


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    iso_639_1 = models.CharField(max_length=10)
    iso_639_2 = models.CharField(max_length=10, blank=True)
    language_name_en = models.CharField(unique=True, max_length=100)

    class Meta:
        db_table = 'list_languages'


class QFEHEALevel(models.Model):
    id = models.AutoField(primary_key=True)
    level = models.CharField(max_length=20)

    class Meta:
        db_table = 'list_qf_ehea_levels'


class Association(models.Model):
    id = models.AutoField(primary_key=True)
    association = models.CharField(max_length=200)

    class Meta:
        db_table = 'list_associations'


class ETEREntity(models.Model):
    id = models.AutoField(primary_key=True)
    eter_id = models.CharField(max_length=25)
    institution_name = models.CharField(max_length=300)

    class Meta:
        db_table = 'list_eter_entities'

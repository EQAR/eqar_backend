from django.db import models


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    iso_639_1 = models.CharField(max_length=10)
    iso_639_2 = models.CharField(max_length=10, blank=True)
    language_name_en = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.language_name_en

    class Meta:
        db_table = 'deqar_list_languages'


class QFEHEALevel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    level = models.CharField(max_length=20)

    def __str__(self):
        return self.level

    class Meta:
        db_table = 'deqar_list_qf_ehea_levels'


class Association(models.Model):
    id = models.AutoField(primary_key=True)
    association = models.CharField(max_length=200)

    def __str__(self):
        return self.association

    class Meta:
        db_table = 'deqar_list_associations'


class EQARDecisionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_list_eqar_decision_types'


class IdentifierResource(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.CharField(max_length=50)

    def __str__(self):
        return self.resource

    class Meta:
        db_table = 'deqar_list_identifier_resources'

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
        verbose_name = 'Language'
        ordering = ('language_name_en',)


class QFEHEALevel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    level = models.CharField(max_length=20)

    def __str__(self):
        return self.level

    class Meta:
        db_table = 'deqar_list_qf_ehea_levels'
        ordering = ('code',)
        verbose_name = 'QF-EHEA level'
        verbose_name_plural = 'QF-EHEA levels'


class Association(models.Model):
    id = models.AutoField(primary_key=True)
    association = models.CharField(max_length=200)

    def __str__(self):
        return self.association

    class Meta:
        db_table = 'deqar_list_associations'
        verbose_name = 'Association'
        ordering = ('association',)


class EQARDecisionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_list_eqar_decision_types'
        verbose_name = 'EQAR Decision Type'
        verbose_name_plural = 'EQAR Decision Types'
        ordering = ('type',)


class IdentifierResource(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.CharField(max_length=50)

    def __str__(self):
        return self.resource

    class Meta:
        db_table = 'deqar_list_identifier_resources'
        verbose_name = 'Identifier Resource'
        verbose_name_plural = 'Identifier Resources'
        ordering = ('resource',)


class PermissionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_list_permission_types'
        verbose_name = 'Permission Type'
        verbose_name_plural = 'Permission Types'
        ordering = ('type',)


class Flag(models.Model):
    id = models.AutoField(primary_key=True)
    flag = models.CharField(max_length=20)

    def __str__(self):
        return self.flag

    class Meta:
        db_table = 'deqar_list_flags'
        verbose_name = 'Flag'
        verbose_name_plural = 'Flags'
        ordering = ('id', 'flag')

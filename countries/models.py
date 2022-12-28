import datetime

from django.contrib.auth.models import User
from django.db import models

from eqar_backend.fields import CharNullField


class Country(models.Model):
    """
    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    """
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('Country', blank=True, null=True, on_delete=models.PROTECT)
    iso_3166_alpha2 = CharNullField(max_length=10, unique=True)
    iso_3166_alpha3 = CharNullField(max_length=3, unique=True)
    name_english = models.CharField(unique=True, max_length=100)
    ehea_is_member = models.BooleanField(default=False)
    eqar_governmental_member_start = models.DateField(blank=True, null=True)
    qa_requirement_note = models.TextField(blank=True)
    external_QAA_is_permitted = models.ForeignKey('lists.PermissionType', related_name='country_external_qaa',
                                                  default=2, on_delete=models.PROTECT)
    external_QAA_note = models.TextField(blank=True, null=True)
    eligibility = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    recognition = models.TextField(blank=True, null=True)
    european_approach_is_permitted = models.ForeignKey('lists.PermissionType', related_name='country_european_approach',
                                                       default=2, on_delete=models.PROTECT)
    european_approach_note = models.TextField(blank=True, null=True)
    general_note = models.TextField(blank=True)
    has_full_institution_list = models.BooleanField(default=False)
    ehea_key_commitment = models.ForeignKey('lists.PermissionType', related_name='country_ehea_key_commitment',
                                            default=2, on_delete=models.PROTECT)
    flag = models.ForeignKey('lists.Flag', default=1, on_delete=models.PROTECT)
    flag_log = models.TextField(blank=True)

    internal_note = models.TextField(blank=True, null=True)

    # OrgReg fields
    orgreg_subcountry_label = CharNullField(max_length=10, blank=True, null=True, unique=True)
    orgreg_eu_2_letter_code = CharNullField(max_length=2, blank=True, null=True, unique=True)
    eu_controlled_vocab_country = CharNullField(max_length=250, blank=True, null=True, unique=True)
    eu_controlled_vocab_atu = CharNullField(max_length=250, blank=True, null=True, unique=True)
    generic_url = models.URLField(max_length=250, blank=True, null=True)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='countries_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name_english

    class Meta:
        db_table = 'deqar_countries'
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ('name_english',)
        indexes = [
            models.Index(fields=['name_english']),
            models.Index(fields=['ehea_is_member']),
            models.Index(fields=['eqar_governmental_member_start']),
            models.Index(fields=['iso_3166_alpha2']),
        ]


class CountryQARequirement(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', on_delete=models.CASCADE)
    qa_requirement = models.CharField(max_length=200)
    qa_requirement_type = models.ForeignKey('countries.CountryQARequirementType', on_delete=models.CASCADE)
    qa_requirement_note = models.TextField(blank=True)
    requirement_valid_from = models.DateField(default=datetime.date.today)
    requirement_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_country_qa_requirements'
        verbose_name = 'Country QA Requirement'
        indexes = [
            models.Index(fields=['requirement_valid_to']),
        ]


class CountryQARequirementType(models.Model):
    """
    Type of country requriement types.
    """
    id = models.AutoField(primary_key=True)
    qa_requirement_type = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.qa_requirement_type

    class Meta:
        db_table = 'deqar_country_qa_requirement_types'
        verbose_name = 'Country QA Requirement Type'


class CountryQAARegulation(models.Model):
    """
    List of QAA regulations imposed on external agencies by individual countries.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', on_delete=models.CASCADE)
    regulation = models.CharField(max_length=200, blank=True)
    regulation_url = models.URLField(max_length=200, blank=True)
    regulation_valid_from = models.DateField(default=datetime.date.today)
    regulation_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_country_qaa_regulations'
        verbose_name = 'Country QAA Regulation'
        indexes = [
            models.Index(fields=['regulation_valid_to']),
        ]


class CountryHistoricalField(models.Model):
    """
    Name of the db_fields which can contain historical data of the country.
    """
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    def __str__(self):
        return self.field

    class Meta:
        db_table = 'deqar_country_historical_fields'
        verbose_name = 'Country Historical Field'
        indexes = [
            models.Index(fields=['field']),
        ]


class CountryHistoricalData(models.Model):
    """
    The historical data that country change.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    field = models.ForeignKey('CountryHistoricalField', on_delete=models.CASCADE)
    record_id = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_country_historical_data'
        verbose_name = 'Country Historical Data'
        indexes = [
            models.Index(fields=['valid_to']),
        ]


class CountryUpdateLog(models.Model):
    """
    Updates happened with a country record
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='country_log_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'deqar_country_update_log'
        verbose_name = 'Country Update Log'
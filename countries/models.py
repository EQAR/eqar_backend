from django.db import models


class Country(models.Model):
    """
    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    """
    id = models.AutoField(primary_key=True)
    iso_3166_alpha2 = models.CharField(max_length=2)
    iso_3166_alpha3 = models.CharField(max_length=3)
    name_english = models.CharField(unique=True, max_length=100)
    ehea_is_member = models.BooleanField(default=False)
    eqar_govermental_member_start = models.DateField(blank=True, null=True)
    qa_requirement = models.CharField(max_length=200, blank=True)
    qa_requirement_type = models.ForeignKey('countries.CountryQARequirementType', on_delete=models.CASCADE)
    qa_requirement_notes = models.TextField(blank=True)
    external_QAA_is_permitted = models.BooleanField(default=False)
    eligibility = models.TextField(blank=True)
    conditions = models.CharField(max_length=200, blank=True)
    recognition = models.CharField(max_length=200, blank=True)
    external_QAA_permitted_note = models.TextField(blank=True)
    european_approach_is_permitted = models.BooleanField(default=False)
    european_approach_note = models.TextField(blank=True)
    general_note = models.TextField(blank=True)

    def __str__(self):
        return self.name_english

    class Meta:
        db_table = 'deqar_counties'


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


class CountryQAARegulation(models.Model):
    """
    List of QAA regulations imposed on external agencies by individual countries.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', on_delete=models.CASCADE)
    regulation = models.CharField(max_length=200, blank=True)
    regulation_url = models.URLField(max_length=200, blank=True)

    class Meta:
        db_table = 'deqar_country_qaa_regulations'


class CountryHistoricalField(models.Model):
    """
    Name of the db_fields which can contain historical data of the country.
    """
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    class Meta:
        db_table = 'deqar_country_historical_fields'


class InstitutionHistoricalData(models.Model):
    """
    The historical data that country change.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    field = models.ForeignKey('CountryHistoricalField', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_country_historical_data'

import datetime
from django.db import models


class Institution(models.Model):
    """
    List of institutions reviewed or evaluated by EQAR registered agencies.
    """
    id = models.AutoField(primary_key=True)
    deqar_id = models.CharField(max_length=25)
    eter = models.ForeignKey('institutions.InstitutionETERRecord', blank=True, null=True, on_delete=models.PROTECT)
    name_primary = models.CharField(max_length=200, blank=True)
    website_link = models.CharField(max_length=150)
    flag = models.ForeignKey('lists.Flag', default=1)

    def __str__(self):
        return self.name_primary

    class Meta:
        db_table = 'deqar_institutions'
        ordering = ('name_primary',)
        indexes = [
            models.Index(fields=['deqar_id']),
            models.Index(fields=['name_primary'])
        ]


class InstitutionIdentifier(models.Model):
    """
    List of other (non-ETER) identifiers for the institution and the source of the identifier.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    agency = models.ForeignKey('agencies.Agency', blank=True, null=True, on_delete=models.SET_NULL)
    resource = models.CharField(max_length=200, blank=True)
    identifier_valid_from = models.DateField(default=datetime.date.today)
    identifier_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_institution_identifiers'
        indexes = [
            models.Index(fields=['identifier_valid_to']),
        ]
        unique_together = ('institution', 'agency', 'resource')


class InstitutionName(models.Model):
    """
    List of names/acronym used for an institution in a particular period.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    name_official = models.CharField(max_length=200)
    name_official_transliterated = models.CharField(max_length=200, blank=True)
    name_english = models.CharField(max_length=200, blank=True)
    acronym = models.CharField(max_length=20, blank=True)
    name_source_note = models.TextField()
    name_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_institution_names'
        ordering = ('institution', 'name_official', 'name_english')
        verbose_name = 'Institution Name'
        verbose_name_plural = 'Institution Names'
        indexes = [
            models.Index(fields=['name_official']),
            models.Index(fields=['name_official_transliterated']),
            models.Index(fields=['name_english']),
            models.Index(fields=['acronym']),
            models.Index(fields=['name_valid_to']),
        ]


class InstitutionNameVersion(models.Model):
    """
    Different versions of institution names with transliteration as applicable.
    """
    id = models.AutoField(primary_key=True)
    institution_name = models.ForeignKey('InstitutionName', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    transliteration = models.CharField(max_length=200, blank=True)
    name_version_source = models.CharField(max_length=20)
    name_version_source_note = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'deqar_institution_name_versions'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['transliteration']),
        ]


class InstitutionCountry(models.Model):
    """
    List of countries where the institution is located.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    country = models.ForeignKey('countries.Country', on_delete=models.PROTECT)
    city = models.CharField(max_length=100, blank=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    country_source = models.CharField(max_length=20)
    country_source_note = models.CharField(max_length=200, blank=True)
    country_valid_from = models.DateField(default=datetime.date.today)
    country_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_institution_countries'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['country_valid_to']),
        ]


class InstitutionNQFLevel(models.Model):
    """
    List of NQF levels that are valid for each institution.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    nqf_level = models.CharField(max_length=10)
    nqf_level_source = models.CharField(max_length=20)
    nqf_level_source_note = models.CharField(max_length=200, blank=True)
    nqf_level_valid_from = models.DateField(default=datetime.date.today)
    nqf_level_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nqf_level

    class Meta:
        db_table = 'deqar_institution_nqf_levels'
        indexes = [
            models.Index(fields=['nqf_level_valid_to']),
        ]


class InstitutionQFEHEALevel(models.Model):
    """
    List of QF-EHEA levels that are valid for each institution.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.PROTECT)
    qf_ehea_level_source = models.CharField(max_length=20)
    qf_ehea_level_source_note = models.CharField(max_length=200, blank=True)
    qf_ehea_level_valid_from = models.DateField(default=datetime.date.today)
    qf_ehea_level_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.qf_ehea_level.level

    class Meta:
        db_table = 'deqar_institution_qf_ehea_levels'
        indexes = [
            models.Index(fields=['qf_ehea_level_valid_to']),
        ]


class InstitutionETERRecord(models.Model):
    """
    Periodically updated list of institutions managed by ETER.
    """
    id = models.AutoField(primary_key=True)
    eter_id = models.CharField(max_length=15)
    national_identifier = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    name_english = models.CharField(max_length=200, blank=True)
    acronym = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=3)
    city = models.CharField(max_length=100, blank=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    website = models.CharField(max_length=200)
    ISCED_lowest = models.CharField(max_length=10)
    ISCED_highest = models.CharField(max_length=10)
    valid_from_year = models.DateField()
    data_updated = models.DateField()
    eter_link = models.URLField(blank=True)

    def __str__(self):
        return "%s - %s" % (self.eter_id, self.name)

    class Meta:
        db_table = 'deqar_institution_eter_records'
        verbose_name = 'ETER Record'
        verbose_name_plural = 'ETER Records'


class InstitutionHistoricalField(models.Model):
    """
    Name of the db_fields which can contain historical data of the institution.
    """
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    def __str__(self):
        return self.field

    class Meta:
        db_table = 'deqar_institution_historical_fields'
        indexes = [
            models.Index(fields=['field']),
        ]


class InstitutionHistoricalData(models.Model):
    """
    The historical data that institutions change.
    """
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    field = models.ForeignKey('InstitutionHistoricalField', on_delete=models.CASCADE)
    record_id = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_institution_historical_data'
        indexes = [
            models.Index(fields=['valid_to']),
        ]
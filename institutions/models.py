from django.db import models


class Institution(models.Model):
    id = models.AutoField(primary_key=True)
    eqar_id = models.CharField(max_length=25)
    eter_id = models.ForeignKey('lists.ETEREntity', blank=True, null=True, on_delete=models.PROTECT)
    website_link = models.CharField(max_length=150)

    class Meta:
        db_table = 'eqar_institutions'


class InstitutionIdentifier(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    agency = models.ForeignKey('agencies.Agency', blank=True, null=True, on_delete=models.SET_NULL)
    resource = models.ForeignKey('InstitutionResource', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_institution_identifiers'


class InstitutionResource(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.CharField(max_length=50)

    class Meta:
        db_table = 'eqar_institution_resources'


class InstitutionName(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    name_official = models.CharField(max_length=200)
    name_official_transliterated = models.CharField(max_length=200, blank=True)
    name_english = models.CharField(max_length=200, blank=True)
    acronym = models.CharField(max_length=20, blank=True)
    source_note = models.TextField(blank=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'eqar_institution_names'


class InstitutionNameVersion(models.Model):
    id = models.AutoField(primary_key=True)
    institution_name = models.ForeignKey('InstitutionName', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    transliteration = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'eqar_institution_name_versions'


class InstitutionCountry(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    country = models.ForeignKey('lists.Country', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_institution_countries'


class InstitutionNQFLevel(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    nqf_level = models.CharField(max_length=10)

    class Meta:
        db_table = 'eqar_institution_nqf_levels'


class InstitutionQFEHEALevel(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_institution_qf_ehea_levels'


class InstitutionHistoricalField(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    class Meta:
        db_table = 'eqar_institution_historical_fields'


class InstitutionHistoricalData(models.Model):
    id = models.AutoField(primary_key=True)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    field = models.ForeignKey('InstitutionHistoricalField', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'eqar_institution_historical_data'

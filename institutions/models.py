import datetime
from django.db import models

from lists.models import Flag


class Institution(models.Model):
    """
    List of institutions reviewed or evaluated by EQAR registered agencies.
    """
    id = models.AutoField(primary_key=True)
    deqar_id = models.CharField(max_length=25, blank=True)
    eter = models.ForeignKey('institutions.InstitutionETERRecord', blank=True, null=True, on_delete=models.PROTECT)
    name_primary = models.CharField(max_length=200, blank=True)
    website_link = models.CharField(max_length=150)
    founding_date = models.DateField(blank=True, null=True)
    closure_date = models.DateField(blank=True, null=True)
    national_identifier = models.CharField(max_length=50, blank=True, null=True)
    source_note = models.TextField(blank=True, null=True)
    flag = models.ForeignKey('lists.Flag', default=1)
    flag_log = models.TextField(blank=True)

    def __str__(self):
        return self.name_primary

    def create_deqar_id(self):
        self.deqar_id = 'DEQARINST%04d' % self.id
        self.save()

    def set_flag_low(self):
        if self.flag_id != 3:
            self.flag = Flag.objects.get(pk=2)
            self.save()

    def set_flag_high(self):
        self.flag = Flag.objects.get(pk=3)
        self.save()

    def set_primary_name(self):
        inst_name_primary = self.institutionname_set.filter(name_valid_to__isnull=True).first()
        if inst_name_primary is not None:
            if inst_name_primary.name_english != "":
                self.name_primary = inst_name_primary.name_english
            else:
                self.name_primary = inst_name_primary.name_official
            self.save()

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
    acronym = models.CharField(max_length=30, blank=True)
    name_source_note = models.TextField()
    name_valid_to = models.DateField(blank=True, null=True)

    def add_source_note(self, flag_msg):
        if flag_msg not in self.name_source_note:
            flag_msg += ' on [%s]' % datetime.date.today().strftime("%Y-%m-%d")
            if len(self.name_source_note) > 0:
                if flag_msg not in self.name_source_note:
                    self.name_source_note += '; %s' % flag_msg
            else:
                self.name_source_note = flag_msg
            self.save()

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
    name_version_source = models.CharField(max_length=20, blank=True)
    name_version_source_note = models.CharField(max_length=200, blank=True)

    def add_source_note(self, flag_msg):
        if flag_msg not in self.name_version_source_note:
            flag_msg += ' on [%s]' % datetime.date.today().strftime("%Y-%m-%d")
            if len(self.name_version_source_note) > 0:
                self.name_version_source_note += '; %s' % flag_msg
            else:
                self.name_version_source_note = flag_msg
            self.save()

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
    country_verified = models.BooleanField(default=True)

    def add_source_note(self, flag_msg):
        if flag_msg not in self.country_source_note:
            flag_msg += ' on [%s]' % datetime.date.today().strftime("%Y-%m-%d")
            if len(self.country_source_note) > 0:
                self.country_source_note += '; %s' % flag_msg
            else:
                self.country_source_note = flag_msg
            self.save()

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

    def add_source_note(self, flag_msg):
        if flag_msg not in self.nqf_level_source_note:
            flag_msg += ' on [%s]' % datetime.date.today().strftime("%Y-%m-%d")
            if len(self.nqf_level_source_note) > 0:
                self.nqf_level_source_note += '; %s' % flag_msg
            else:
                self.nqf_level_source_note = flag_msg
            self.save()

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
    qf_ehea_level_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.qf_ehea_level.level

    def add_source_note(self, flag_msg):
        if flag_msg not in self.qf_ehea_level_source_note:
            flag_msg += ' on [%s]' % datetime.date.today().strftime("%Y-%m-%d")
            if len(self.qf_ehea_level_source_note) > 0:
                self.qf_ehea_level_source_note += '; %s' % flag_msg
            else:
                self.qf_ehea_level_source_note = flag_msg
            self.save()

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

    def create_institution_from_eter(self):
        Institution(
            eter_id=self.eter_id,
            name_primary=self.name_english,
            website_link=self.website
        )

    class Meta:
        db_table = 'deqar_institution_eter_records'
        verbose_name = 'ETER Record'
        verbose_name_plural = 'ETER Records'


class InstitutionHistoricalRelationshipType(models.Model):
    """
    Historical relationship types between institutions
    """
    id = models.AutoField(primary_key=True)
    type_from = models.CharField(max_length=200)
    type_to = models.CharField(max_length=200)

    def __str__(self):
        return "=> %s / %s <=" % (self.type_from, self.type_to)

    class Meta:
        db_table = 'deqar_institution_historical_relationship_types'
        verbose_name = 'Institution Historical Relationship Type'
        verbose_name_plural = 'Institution Historical Relationship Types'


class InstitutionHistoricalRelationship(models.Model):
    """
    Historical relationships between institutions
    """
    id = models.AutoField(primary_key=True)
    institution_source = models.ForeignKey('Institution', related_name='relationship_source', on_delete=models.CASCADE)
    institution_target = models.ForeignKey('Institution', related_name='relationship_target', on_delete=models.CASCADE)
    relationship_type = models.ForeignKey('InstitutionHistoricalRelationshipType', on_delete=models.CASCADE)
    relationship_note = models.CharField(max_length=300, blank=True, null=True)
    relationship_date = models.DateField(default=datetime.date.today)

    class Meta:
        db_table = 'deqar_institution_historical_relationships'
        verbose_name = 'Institution Historical Relationship'
        verbose_name_plural = 'Institution Historical Relationships'


class InstitutionHierarchicalRelationship(models.Model):
    """
    Hierarchival relationships between institutions
    """
    id = models.AutoField(primary_key=True)
    institution_parent = models.ForeignKey('Institution', related_name='relationship_parent', on_delete=models.CASCADE)
    institution_child = models.ForeignKey('Institution', related_name='relationship_child', on_delete=models.CASCADE)
    relationship_note = models.CharField(max_length=300, blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_institution_hierarchical_relationships'
        verbose_name = 'Institution Hierarchical Relationship'
        verbose_name_plural = 'Institution Hierarchical Relationships'


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
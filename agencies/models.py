from django.db import models


class Agency(models.Model):
    """
    List of registered EQAR agencies.
    """
    id = models.AutoField(primary_key=True)
    deqar_id = models.CharField(max_length=25)
    name_primary = models.CharField(max_length=200, blank=True)
    acronym_primary = models.CharField(max_length=20, blank=True)
    contact_person = models.CharField(max_length=150)
    fax = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    country = models.ForeignKey('countries.Country', blank=True, null=True)
    website_link = models.URLField(max_length=100)
    logo = models.FileField(blank=True, null=True)
    geographical_focus = models.ForeignKey('AgencyGeographicalFocus', blank=True, null=True)
    specialisation_note = models.TextField(blank=True)
    reports_link = models.URLField(blank=True, null=True)
    description_note = models.TextField()
    registration_start = models.DateField()
    registration_valid_to = models.DateField()
    registration_note = models.TextField(blank=True)
    related_agencies = models.ManyToManyField('self', through='AgencyRelationship', symmetrical=False)

    def __str__(self):
        return "%s - %s" % (self.get_primary_acronym(), self.get_primary_name())

    def get_primary_name(self):
        anv = AgencyNameVersion.objects.filter(agency_name__in=self.agencyname_set.all(), name_is_primary=True).first()
        return anv.name

    def get_primary_acronym(self):
        anv = AgencyNameVersion.objects.filter(agency_name__in=self.agencyname_set.all(), acronym_is_primary=True).first()
        return anv.acronym

    class Meta:
        db_table = 'deqar_agencies'
        ordering = ('acronym_primary', 'name_primary')


class AgencyGeographicalFocus(models.Model):
    """
    List of the agency focus level.
    """
    id = models.AutoField(primary_key=True)
    focus = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.focus

    class Meta:
        db_table = 'deqar_agency_geographical_focuses'


class AgencyName(models.Model):
    """
    List of agency names/acronyms in a particular period.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    name_note = models.TextField(blank=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_names'


class AgencyNameVersion(models.Model):
    """
    Different versions of agency names with transliteration as applicable.
    """
    id = models.AutoField(primary_key=True)
    agency_name = models.ForeignKey('AgencyName', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    name_transliterated = models.CharField(max_length=200, blank=True)
    name_is_primary = models.BooleanField(default=False)
    acronym = models.CharField(max_length=20, blank=True)
    acronym_transliterated = models.CharField(max_length=20, blank=True)
    acronym_is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'deqar_agency_name_versions'
        ordering = ('name_is_primary', 'name')


class AgencyPhone(models.Model):
    """
    One or more phone numbers for each agency.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'deqar_agency_phones'
        unique_together = ('agency', 'phone')


class AgencyEmail(models.Model):
    """
    One or more contact emails for each agency.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    email = models.CharField(max_length=50)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'deqar_agency_emails'
        unique_together = ('agency', 'email')
        ordering = ('email',)


class AgencyFocusCountry(models.Model):
    """
    List of EHEA countries where the agency has evaluated,
    accredited or audited higher education institutions or programmes.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    country = models.ForeignKey('countries.Country', on_delete=models.PROTECT)
    country_is_official = models.BooleanField(default=False)

    def __str__(self):
        return self.country.name_english

    class Meta:
        db_table = 'deqar_agency_focus_countries'
        unique_together = ('agency', 'country')
        ordering = ('country__name_english',)


class AgencyESGActivity(models.Model):
    """
    External quality assurance activities in the scope of the ESG.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    activity = models.CharField(max_length=200)
    activity_local_identifier = models.CharField(max_length=20, blank=True)
    activity_description = models.CharField(max_length=300, blank=True)
    activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)
    reports_link = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_esg_activities'


class AgencyActivityType(models.Model):
    """
    Agency activity types.
    """
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_agency_activity_types'


class AgencyRelationship(models.Model):
    """
    Mergers, spin offs and other historical events which link two agencies.
    """
    from_agency = models.ForeignKey('Agency', related_name='from_agencies', on_delete=models.CASCADE)
    to_agency = models.ForeignKey('Agency', related_name='to_agencies', on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField()

    class Meta:
        db_table = 'deqar_agency_relationships'
        unique_together = ('from_agency', 'to_agency')


class AgencyMembership(models.Model):
    """
    List of associations to which each agency belongs.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    association = models.ForeignKey('lists.Association', on_delete=models.PROTECT)

    def __str__(self):
        return self.association.association

    class Meta:
        db_table = 'deqar_agency_memberships'
        unique_together = ('agency', 'association')


class AgencyEQARDecision(models.Model):
    """
    List of EQAR register decision dates for each agency with any connected reports.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    decision_date = models.DateField()
    decision_type = models.ForeignKey('lists.EQARDecisionType')
    decision_file = models.FileField()
    decision_file_extra = models.FileField(blank=True)

    class Meta:
        db_table = 'deqar_agency_eqar_decisions'


class AgencyHistoricalField(models.Model):
    """
    Name of the db_fields which can contain historical data.
    This will save changed data from named fields.
    """
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    def __str__(self):
        return self.field

    class Meta:
        db_table = 'deqar_agency_historical_fields'


class AgencyHistoricalData(models.Model):
    """
    The historical data that agencies change.
    Either valid from or valid to date must be filled.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    field = models.ForeignKey('AgencyHistoricalField', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agecy_historical_data'

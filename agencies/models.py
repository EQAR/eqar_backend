from django.db import models


class Agency(models.Model):
    id = models.AutoField(primary_key=True)
    eqar_id = models.CharField(max_length=25)
    contact_person = models.CharField(max_length=150)
    fax = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    country = models.ForeignKey('lists.Country', blank=True, null=True)
    website_link = models.URLField(max_length=100)
    specialisation_note = models.TextField(blank=True)
    activity_note = models.TextField(blank=True)
    reports_link = models.URLField()
    description_note = models.TextField()
    registration_start = models.DateField()
    registration_valid_to = models.DateField()
    registration_note = models.TextField(blank=True)
    focus = models.ForeignKey('AgencyFocus', blank=True, null=True)
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
        db_table = 'eqar_agencies'


class AgencyFocus(models.Model):
    id = models.AutoField(primary_key=True)
    focus = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.focus

    class Meta:
        db_table = 'eqar_agency_focuses'


class AgencyENQUAMembership(models.Model):
    id = models.AutoField(primary_key=True)
    membership = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.membership

    class Meta:
        db_table = 'eqar_agency_enqua_memberships'


class AgencyName(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    name_note = models.TextField(blank=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'eqar_agency_names'


class AgencyNameVersion(models.Model):
    id = models.AutoField(primary_key=True)
    agency_name = models.ForeignKey('AgencyName', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    name_transliterated = models.CharField(max_length=200, blank=True)
    name_is_primary = models.BooleanField(default=False)
    acronym = models.CharField(max_length=20, blank=True)
    acronym_transliterated = models.CharField(max_length=20, blank=True)
    acronym_is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'eqar_agency_name_versions'


class AgencyPhone(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'eqar_agency_phones'
        unique_together = ('agency', 'phone')


class AgencyEmail(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    email = models.CharField(max_length=50)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'eqar_agency_emails'
        unique_together = ('agency', 'email')


class AgencyFocusCountry(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    country = models.ForeignKey('lists.Country', on_delete=models.PROTECT)
    focus_country_official = models.BooleanField(default=False)

    def __str__(self):
        return self.country.country_name_en

    class Meta:
        db_table = 'eqar_agency_focus_countries'
        unique_together = ('agency', 'country')


class AgencyESGActivity(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    activity_description = models.CharField(max_length=300, blank=True)
    esg_activity = models.CharField(max_length=200)
    activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_agency_esga_activities'


class AgencyActivityType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'eqar_agency_activity_types'


class AgencyRelationship(models.Model):
    from_agency = models.ForeignKey('Agency', related_name='from_agencies', on_delete=models.CASCADE)
    to_agency = models.ForeignKey('Agency', related_name='to_agencies', on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField()

    class Meta:
        db_table = 'eqar_agency_relationships'
        unique_together = ('from_agency', 'to_agency')


class AgencyMembership(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    association = models.ForeignKey('lists.Association', on_delete=models.PROTECT)

    def __str__(self):
        return self.association.association

    class Meta:
        db_table = 'eqar_agency_memberships'
        unique_together = ('agency', 'association')


class AgencyEQARDecision(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    decision_date = models.DateField()
    decision_type = models.ForeignKey('lists.EQARDecisionType')
    decision_file = models.FileField()
    decision_file_extra = models.FileField(blank=True)

    class Meta:
        db_table = 'eqar_agency_eqar_decisions'


class AgencyHistoricalField(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

    def __str__(self):
        return self.field

    class Meta:
        db_table = 'eqar_agency_historical_fields'


class AgencyHistoricalData(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    field = models.ForeignKey('AgencyHistoricalField', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'eqar_agecy_historical_data'

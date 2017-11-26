from django.db import models


class Agency(models.Model):
    id = models.AutoField(primary_key=True)
    eqar_id = models.CharField(max_length=25)
    contact_person = models.CharField(max_length=150)
    fax = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    website_link = models.URLField(max_length=100)
    specialisation_note = models.TextField(blank=True)
    activity_note = models.TextField(blank=True)
    reports_link = models.URLField()
    description_note = models.TextField()
    registration_start = models.DateField()
    registration_valid_to = models.DateField()
    registration_note = models.TextField(blank=True)
    focus = models.ForeignKey('AgencyFocus', blank=True, null=True)
    enqua_membership = models.ForeignKey('AgencyENQUAMembership')
    related_agencies = models.ManyToManyField('self', through='AgencyRelationship', symmetrical=False)

    class Meta:
        db_table = 'eqar_agencies'


class AgencyFocus(models.Model):
    id = models.AutoField(primary_key=True)
    focus = models.CharField(max_length=20)

    class Meta:
        db_table = 'eqar_agency_focuses'


class AgencyENQUAMembership(models.Model):
    id = models.AutoField(primary_key=True)
    membership = models.CharField(max_length=20)

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

    class Meta:
        db_table = 'eqar_agency_phones'


class AgencyEmail(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    email = models.CharField(max_length=50)

    class Meta:
        db_table = 'eqar_agency_emails'


class AgencyLocationCountry(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    country = models.ForeignKey('lists.Country', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_agency_location_countries'


class AgencyFocusCountry(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    country = models.ForeignKey('lists.Country', on_delete=models.PROTECT)
    focus_country_official = models.BooleanField(default=False)

    class Meta:
        db_table = 'eqar_agency_focus_countries'


class AgencyESGActivities(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    activity_description = models.CharField(max_length=300, blank=True)
    esg_activity = models.CharField(max_length=200)
    activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_agency_esga_activities'


class AgencyActivityType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20)

    class Meta:
        db_table = 'eqar_agency_activity_types'


class AgencyLevels(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_agency_levels'


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
    associaton = models.ForeignKey('lists.Association', on_delete=models.PROTECT)

    class Meta:
        db_table = 'eqar_agency_memberships'


class AgencyEQARRenewal(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    renewal_date = models.DateField()
    review_report_file = models.FileField(blank=True)
    decision_file = models.FileField(blank=True)

    class Meta:
        db_table = 'eqar_agency_eqar_renewals'


class AgencyEQARChange(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    change_date = models.DateField()
    change_report_file = models.FileField()

    class Meta:
        db_table = 'eqar_agency_eqar_changes'


class AgencyHistoricalField(models.Model):
    id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=50)

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

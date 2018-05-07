import datetime
from datetime import date

from django.db import models
from django.db.models import Q


class Agency(models.Model):
    """
    List of registered EQAR agencies.
    """
    id = models.AutoField(primary_key=True)
    deqar_id = models.IntegerField()
    name_primary = models.CharField(max_length=200, blank=True)
    acronym_primary = models.CharField(max_length=20, blank=True)
    contact_person = models.CharField(max_length=150)
    fax = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    country = models.ForeignKey('countries.Country')
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
    flag = models.ForeignKey('lists.Flag', default=1)
    flag_log = models.TextField(blank=True)

    def __str__(self):
        return "%s - %s" % (self.acronym_primary, self.name_primary)

    def get_primary_name(self):
        anv = AgencyNameVersion.objects.filter(agency_name__in=self.agencyname_set.all(),
                                               agency_name__name_valid_to__isnull=True,
                                               name_is_primary=True).first()
        return anv.name if anv else ""

    def get_primary_acronym(self):
        anv = AgencyNameVersion.objects.filter(agency_name__in=self.agencyname_set.all(),
                                               agency_name__name_valid_to__isnull=True,
                                               acronym_is_primary=True).first()
        return anv.acronym if anv else ""

    class Meta:
        db_table = 'deqar_agencies'
        ordering = ('acronym_primary', 'name_primary')
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
        indexes = [
            models.Index(fields=['name_primary']),
            models.Index(fields=['acronym_primary']),
            models.Index(fields=['registration_valid_to']),
        ]


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
    name_valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_names'
        verbose_name = 'Agency Name'
        verbose_name_plural = 'Agency Names'
        indexes = [
            models.Index(fields=['name_valid_to'])
        ]


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
    country_is_crossborder = models.BooleanField(default=False)
    country_valid_from = models.DateField(default=datetime.date.today)
    country_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.country.name_english

    class Meta:
        db_table = 'deqar_agency_focus_countries'
        unique_together = ('agency', 'country')
        ordering = ('country__name_english',)
        indexes = [
            models.Index(fields=['country_is_crossborder']),
            models.Index(fields=['country_valid_to'])
        ]


class AgencyESGActivity(models.Model):
    """
    External quality assurance activities in the scope of the ESG.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    activity = models.CharField(max_length=500)
    activity_local_identifier = models.CharField(max_length=100, blank=True)
    activity_description = models.CharField(max_length=300, blank=True)
    activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)
    reports_link = models.URLField(blank=True, null=True)
    activity_valid_from = models.DateField(default=date.today)
    activity_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s -> %s (%s)" % (self.agency.acronym_primary, self.activity, self.activity_type)

    class Meta:
        db_table = 'deqar_agency_esg_activities'
        ordering = ('agency', 'activity')
        indexes = [
            models.Index(fields=['activity_valid_to'])
        ]


class AgencyActivityType(models.Model):
    """
    Agency activity types.
    """
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_agency_activity_types'


class AgencyRelationship(models.Model):
    """
    Mergers, spin offs and other historical events which link two agencies.
    """
    id = models.AutoField(primary_key=True)
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
    membership_valid_from = models.DateField(default=datetime.date.today)
    membership_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.association.association

    class Meta:
        db_table = 'deqar_agency_memberships'
        unique_together = ('agency', 'association')
        indexes = [
            models.Index(fields=['membership_valid_to'])
        ]


class AgencyEQARDecision(models.Model):
    """
    List of EQAR register decision dates for each agency with any connected reports.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    decision_date = models.DateField()
    decision_type = models.ForeignKey('lists.EQARDecisionType')
    decision_file = models.FileField(upload_to='EQAR/')
    decision_file_extra = models.FileField(blank=True, upload_to='EQAR/')

    class Meta:
        db_table = 'deqar_agency_eqar_decisions'


class SubmittingAgency(models.Model):
    """
    List of agencies registered to submit data to DEQAR.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, blank=True, null=True)
    external_agency = models.CharField(max_length=200, blank=True)
    external_agency_acronym = models.CharField(max_length=20, blank=True)
    registration_from = models.DateField(default=datetime.date.today)
    registration_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_submitting_agencies'
        verbose_name = 'Submitting Agency'
        verbose_name_plural = 'Submitting Agencies'

    def __str__(self):
        if self.agency:
            return str(self.agency)
        else:
            return "%s - %s" % (self.external_agency_acronym, self.external_agency)

    def agency_allowed(self, agency):
        ap = AgencyProxy.objects.filter(
            Q(submitting_agency=self) & Q(allowed_agency=agency) &
            (
                Q(proxy_to__isnull=True) | Q(proxy_to__lte=datetime.datetime.now())
            )
        ).count()
        return ap > 0


class AgencyProxy(models.Model):
    """
    List of EQAR registered agencies whose data is submitted to DEQAR by a different submitting agency.
    """
    id = models.AutoField(primary_key=True)
    submitting_agency = models.ForeignKey('SubmittingAgency', on_delete=models.CASCADE, related_name='submitting_agency')
    allowed_agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='allowed_agency')
    proxy_from = models.DateField(default=datetime.date.today)
    proxy_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_agency_proxies'
        unique_together = ('submitting_agency', 'allowed_agency')
        indexes = [
            models.Index(fields=['proxy_to'])
        ]


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
        indexes = [
            models.Index(fields=['field'])
        ]


class AgencyHistoricalData(models.Model):
    """
    The historical data that agencies change.
    Either valid from or valid to date must be filled.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    field = models.ForeignKey('AgencyHistoricalField', on_delete=models.CASCADE)
    record_id = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=200)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_historical_data'
        indexes = [
            models.Index(fields=['valid_to'])
        ]

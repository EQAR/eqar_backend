import datetime
from datetime import date

import celery
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


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
    country = models.ForeignKey('countries.Country', on_delete=models.PROTECT)
    website_link = models.URLField(max_length=100)
    logo = models.FileField(blank=True, null=True)
    geographical_focus = models.ForeignKey('AgencyGeographicalFocus', blank=True, null=True, on_delete=models.SET_NULL)
    specialisation_note = models.TextField(blank=True)
    reports_link = models.URLField(blank=True, null=True)
    description_note = models.TextField()
    is_registered = models.BooleanField(default=True)
    registration_start = models.DateField(blank=True, null=True)
    registration_valid_to = models.DateField(blank=True, null=True)
    registration_note = models.TextField(blank=True)
    related_agencies = models.ManyToManyField('self', through='AgencyRelationship', symmetrical=False)
    flag = models.ForeignKey('lists.Flag', default=1, on_delete=models.PROTECT)
    flag_log = models.TextField(blank=True)
    internal_note = models.TextField(blank=True, null=True)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='agencies_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

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
        verbose_name = 'Agency Geographical Focus'
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

    def save(self, *args, **kwargs):
        super(AgencyNameVersion, self).save(*args, **kwargs)
        new_name_primary = self.agency_name.agency.get_primary_name()
        new_acronym_primary = self.agency_name.agency.get_primary_acronym()

        if self.agency_name.agency.name_primary != new_name_primary or \
           self.agency_name.agency.acronym_primary != new_acronym_primary:
            self.agency_name.agency.name_primary = new_name_primary
            self.agency_name.agency.acronym_primary = new_acronym_primary
            self.agency_name.agency.save()
            celery.current_app.send_task('agencies.tasks.index_reports_when_agency_acronym_changes',
                                         (self.agency_name.agency.id,))
            celery.current_app.send_task('agencies.tasks.index_institutions_when_agency_acronym_changes',
                                         (self.agency_name.agency.id,))

    class Meta:
        db_table = 'deqar_agency_name_versions'
        verbose_name = 'Agency Name Version'
        ordering = ('-name_is_primary', 'name')


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
        verbose_name = 'Agency Phone'
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
        verbose_name = 'Agency Email'
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
        verbose_name = 'Agency Focus Country'
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
    activity = models.CharField(max_length=500, blank=True, null=True)
    activity_group = models.ForeignKey('AgencyActivityGroup', on_delete=models.PROTECT)
    activity_display = models.CharField(max_length=500, blank=True, null=True)
    activity_local_identifier = models.CharField(max_length=100, blank=True)
    activity_description = models.CharField(max_length=300, blank=True)
    # activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)
    reports_link = models.URLField(blank=True, null=True)
    activity_valid_from = models.DateField(default=date.today)
    activity_valid_to = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.activity_display:
            return self.activity_display
        else:
            if self.activity:
                return self.activity
            else:
                return self.activity_group.activity

    @property
    def activity_type(self):
        return self.activity_group.activity_type

    @property
    def activity_type_id(self):
        return self.activity_group.activity_type_id

    def set_activity_display(self):
        self.activity_display = "%s -> %s (%s)" % (self.agency.acronym_primary, self.activity, self.activity_type)

    def validate_local_identifier(self):
        if self.activity_local_identifier != '':
            conflicting_instance = AgencyESGActivity.objects.filter(agency=self.agency,
                                                                    activity_local_identifier=self.activity_local_identifier)
            if self.id:
                conflicting_instance = conflicting_instance.exclude(pk=self.id)

            if conflicting_instance.exists():
                raise ValidationError('ESG Activity with this name and parent already exists.')

    def save(self, *args, **kwargs):
        self.set_activity_display()
        self.validate_local_identifier()
        super(AgencyESGActivity, self).save(*args, **kwargs)

    class Meta:
        db_table = 'deqar_agency_esg_activities'
        verbose_name = 'ESG Activity'
        verbose_name_plural = 'ESG Activities'
        ordering = ('agency', 'activity')
        indexes = [
            models.Index(fields=['activity_display']),
            models.Index(fields=['activity_valid_to'])
        ]


class AgencyActivityGroup(models.Model):
    """
       External quality assurance activity groups.
       """
    id = models.AutoField(primary_key=True)
    activity = models.CharField(max_length=500)
    activity_type = models.ForeignKey('AgencyActivityType', on_delete=models.PROTECT)
    reports_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return "%s (%s)" % (self.activity, self.activity_type)

    class Meta:
        ordering = ('activity', 'activity_type')
        db_table = 'deqar_agency_activity_group'
        verbose_name = 'ESG Activity Group'


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
        verbose_name = 'Agency Activity Type'


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
        verbose_name = 'Agency Relationship'
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
        verbose_name = 'Agency Membership'
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
    decision_type = models.ForeignKey('lists.EQARDecisionType', on_delete=models.PROTECT)
    decision_file = models.FileField(upload_to='EQAR/')
    decision_file_extra = models.FileField(blank=True, upload_to='EQAR/')

    class Meta:
        db_table = 'deqar_agency_eqar_decisions'
        verbose_name = 'Agency EQAR Decision'


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
        verbose_name = 'Agency Proxy'
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
        verbose_name = 'Agency Historical Field'
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
        verbose_name = 'Agency Historical Data'
        indexes = [
            models.Index(fields=['valid_to'])
        ]


class AgencyFlag(models.Model):
    """
    Flags belonging to an agency
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    flag = models.ForeignKey('lists.Flag', on_delete=models.PROTECT)
    flag_message = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    removed_by_eqar = models.BooleanField(default=False)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deqar_agency_flags'
        verbose_name = 'Agency Flag'
        ordering = ['id', 'flag__id']
        unique_together = ['agency', 'flag_message']


class AgencyUpdateLog(models.Model):
    """
    Updates happened with an agency
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='agency_log_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'deqar_agency_update_log'
        verbose_name = 'Agency Update Log'

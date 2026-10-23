import datetime
import re

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constraints import UniqueConstraint

from eqar_backend.fields.char_null_field import CharNullField


class Country(models.Model):
    """
    Countries related to HE institutions, EQAR agencies and other QA activities.
    Includes information on QA requirements imposed in the country.
    """
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('Country', blank=True, null=True, on_delete=models.PROTECT)
    iso_3166_alpha2 = models.CharField(max_length=10, unique=True)
    iso_3166_alpha3 = models.CharField(max_length=3, blank=True, null=True, unique=True)
    name_english = models.CharField(unique=True, max_length=100)
    ehea_is_member = models.BooleanField(default=False)
    eqar_governmental_member_start = models.DateField(blank=True, null=True)
    qa_requirement_note = models.TextField(blank=True)
    external_QAA_is_permitted = models.ForeignKey('lists.PermissionType', related_name='country_external_qaa',
                                                  default=2, on_delete=models.PROTECT)
    european_approach_is_permitted = models.ForeignKey('lists.PermissionType', related_name='country_european_approach',
                                                       default=2, on_delete=models.PROTECT)
    general_note = models.TextField(blank=True)
    lrc_signatory_date = models.DateField(blank=True, null=True, verbose_name='LRC signatory date',
                                          help_text='when the country signed the Lisbon Recognition Convention; '
                                                    'empty if it has not signed')
    qf_ehea_alignment_date = models.DateField(blank=True, null=True, verbose_name='QF-EHEA alignment date',
                                              help_text='when the country self-certified its NQF against the '
                                                        'QF-EHEA; empty if it has not')
    eqf_alignment_date = models.DateField(blank=True, null=True, verbose_name='EQF alignment date',
                                          help_text='when the country referenced its NQF against the EQF; '
                                                    'empty if it has not')
    has_full_institution_list = models.BooleanField(default=False)
    ehea_key_commitment = models.ForeignKey('lists.PermissionType', related_name='country_ehea_key_commitment',
                                            default=2, on_delete=models.PROTECT)
    flag = models.ForeignKey('lists.Flag', default=1, on_delete=models.PROTECT)
    flag_log = models.TextField(blank=True)

    internal_note = models.TextField(blank=True, null=True)

    # OrgReg fields
    orgreg_subcountry_label = CharNullField(max_length=200, blank=True, null=True)
    orgreg_eu_2_letter_code = models.CharField(max_length=3, blank=True, null=True, unique=True)
    eu_controlled_vocab_country = models.CharField(max_length=250, blank=True, null=True, unique=True)
    eu_controlled_vocab_atu = models.CharField(max_length=250, blank=True, null=True, unique=True)
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
        constraints = [
            UniqueConstraint(fields=['parent', 'orgreg_subcountry_label'],
                             name='orgreg_subcountry_unique')
        ]
        indexes = [
            models.Index(fields=['name_english']),
            models.Index(fields=['ehea_is_member']),
            models.Index(fields=['eqar_governmental_member_start']),
            models.Index(fields=['iso_3166_alpha2']),
        ]


class CountryQARequirementGroup(models.Model):
    """
    One or more institution types of a country that share common QA requirements,
    including their possibilities for outgoing TNE and micro-credentials.
    """
    COMBINATION_LOGIC_CHOICES = (
        ('AND', 'cumulative (AND)'),
        ('OR', 'alternative (OR)'),
    )

    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', related_name='qa_requirement_groups', on_delete=models.CASCADE)
    institution_types = models.ManyToManyField('countries.CountryInstitutionType', blank=True,
                                               related_name='qa_requirement_groups')
    combination_logic = models.CharField(max_length=3, choices=COMBINATION_LOGIC_CHOICES, default='AND',
                                         help_text='whether the requirements in this group are cumulative or '
                                                   'alternative')

    # outgoing transnational education
    outgoing_tne_possible = models.ForeignKey('lists.TnePossible', related_name='+', on_delete=models.PROTECT,
                                              blank=True, null=True, verbose_name='outgoing TNE possible',
                                              help_text='whether HEIs can offer TNE in other systems')
    outgoing_tne_conditions = models.TextField(blank=True, verbose_name='outgoing TNE conditions')
    outgoing_tne_approval = models.ManyToManyField('lists.TneApprovalOutgoing', blank=True, related_name='+',
                                                   verbose_name='outgoing TNE approval needed')
    outgoing_tne_qa = models.ForeignKey('lists.TneQaOutgoing', related_name='+', on_delete=models.PROTECT,
                                        blank=True, null=True, verbose_name='outgoing TNE QA regime')

    # micro-credentials
    mc_possible = models.BooleanField(default=False, verbose_name='MC possible',
                                      help_text='HEIs in this group can award micro-credentials that are linked to '
                                                'the QF-EHEA or bear ECTS credits')
    mc_credit_limit = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='MC credit limit',
                                                       help_text='upper limit of ECTS for a micro-credential')
    mc_qa = models.ManyToManyField('lists.McQa', blank=True, related_name='+', verbose_name='MC QA regime')
    mc_qa_note = models.TextField(blank=True, verbose_name='MC QA notes')

    def __str__(self):
        if self.pk:
            types = ', '.join(str(t) for t in self.institution_types.all())
            if types:
                return types
            return f'QA requirements group #{self.pk}'
        return 'New QA requirements group'

    class Meta:
        db_table = 'deqar_country_qa_requirement_groups'
        verbose_name = 'Country QA Requirements Group'
        ordering = ('id',)


class CountryQARequirement(models.Model):
    """
    A specific QA requirement that applies to a group of institution types.
    """
    # requirements tied to purely institutional activities do not have a programme scope
    INSTITUTIONAL_ACTIVITY_TYPE_ID = 2
    # lists.CrossBorderPossibility 'Not possible': CBQA criteria and recognition do not apply
    CBQA_NOT_POSSIBLE_ID = 1
    ISCED_F_BASE_URI = 'http://data.europa.eu/esco/isced-f/'

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey('countries.CountryQARequirementGroup', related_name='requirements',
                              on_delete=models.CASCADE)
    activity_group = models.ForeignKey('agencies.AgencyActivityGroup', related_name='country_qa_requirements',
                                       on_delete=models.PROTECT, blank=True, null=True,
                                       verbose_name='ESG activity group',
                                       help_text='the type of QA review that needs to be passed to satisfy '
                                                 'this requirement')
    duration = models.PositiveSmallIntegerField(blank=True, null=True,
                                                help_text='validity or length of accreditation cycles, in months')
    initial_only = models.BooleanField(default=False,
                                       help_text='requirement only applies to new institutions/programmes '
                                                 'initially, rather than cyclically')

    # programme scope (not applicable to purely institutional activities)
    fields_of_education = ArrayField(models.CharField(max_length=70), default=list, blank=True,
                                     help_text='ISCED-F codes or URIs, separated by commas; '
                                               'empty if the requirement applies to all fields')
    qf_ehea_levels = models.ManyToManyField('lists.QFEHEALevel', blank=True, related_name='+',
                                            verbose_name='QF-EHEA levels',
                                            help_text='empty if the requirement applies to all levels')
    full_degrees = models.BooleanField(default=True)
    micro_credentials = models.BooleanField(default=False)

    qa_requirement_note = models.TextField(blank=True, verbose_name='notes')
    requirement_valid_from = models.DateField(default=datetime.date.today, verbose_name='valid from')
    requirement_valid_to = models.DateField(blank=True, null=True, verbose_name='valid to')

    # cross-border QA
    cbqa_possible = models.ForeignKey('lists.CrossBorderPossibility', related_name='+', on_delete=models.PROTECT,
                                      blank=True, null=True, verbose_name='CBQA possible')
    cbqa_approval = models.ManyToManyField('lists.CrossBorderApproval', blank=True, related_name='+',
                                           verbose_name='CBQA approval needed')
    cbqa_requirements = models.ManyToManyField('lists.CrossBorderRequirement', blank=True, related_name='+',
                                               verbose_name='CBQA requirements')
    cbqa_other_requirements_note = models.TextField(blank=True, verbose_name='CBQA other requirements note')
    cbqa_criteria = models.ForeignKey('lists.CrossBorderCriteria', related_name='+', on_delete=models.PROTECT,
                                      blank=True, null=True, verbose_name='CBQA criteria')
    cbqa_recognition = models.ForeignKey('lists.CrossBorderDecision', related_name='+', on_delete=models.PROTECT,
                                         blank=True, null=True, verbose_name='CBQA recognition')

    # European Approach (not applicable to purely institutional activities)
    ea_possible = models.ForeignKey('lists.EuropeanApproachPossibility', related_name='+', on_delete=models.PROTECT,
                                    blank=True, null=True, verbose_name='EA possible')
    ea_note = models.TextField(blank=True, verbose_name='EA note')

    def __str__(self):
        return str(self.activity_group or f'QA requirement #{self.pk}')

    @property
    def country(self):
        return self.group.country

    @property
    def is_institutional(self):
        return self.activity_group is not None and \
            self.activity_group.activity_type_id == self.INSTITUTIONAL_ACTIVITY_TYPE_ID

    @classmethod
    def normalize_isced_f(cls, value):
        """
        Returns the ISCED-F URI for a code or URI, or None if the value is not valid.
        """
        value = value.strip()
        if re.fullmatch(r'[0-9]{1,4}', value):
            return cls.ISCED_F_BASE_URI + value
        if re.fullmatch(re.escape(cls.ISCED_F_BASE_URI) + r'[0-9]{1,4}', value):
            return value
        return None

    def clean(self):
        errors = {}

        fields_of_education = []
        for value in self.fields_of_education or []:
            uri = self.normalize_isced_f(value)
            if uri is None:
                errors.setdefault('fields_of_education', []).append(
                    f'"{value}" is not a valid ISCED-F code (max. 4 digits) or URI.')
            elif uri not in fields_of_education:
                fields_of_education.append(uri)
        self.fields_of_education = fields_of_education

        if self.is_institutional:
            if self.fields_of_education:
                errors.setdefault('fields_of_education', []).append(
                    'Fields of education only apply to programme-related activities.')
            if self.ea_possible_id is not None:
                errors['ea_possible'] = 'The European Approach only applies to programme-related activities.'
            if self.ea_note:
                errors['ea_note'] = 'The European Approach only applies to programme-related activities.'
        elif not (self.full_degrees or self.micro_credentials):
            errors['micro_credentials'] = 'The requirement needs to apply to full degrees, micro-credentials or both.'

        if self.requirement_valid_to and self.requirement_valid_from and \
                self.requirement_valid_to < self.requirement_valid_from:
            errors['requirement_valid_to'] = 'End date cannot be before start date.'

        # mandatory for new requirements; legacy requirements may still lack them until enriched
        if self._state.adding:
            for field in ('activity_group', 'cbqa_possible'):
                if getattr(self, f'{field}_id') is None:
                    errors[field] = 'This field is required.'
            if self.cbqa_possible_id is not None and self.cbqa_possible_id != self.CBQA_NOT_POSSIBLE_ID:
                for field in ('cbqa_criteria', 'cbqa_recognition'):
                    if getattr(self, f'{field}_id') is None:
                        errors[field] = 'This field is required if cross-border QA is possible.'
            if self.activity_group_id is not None and not self.is_institutional and self.ea_possible_id is None:
                errors['ea_possible'] = 'This field is required for programme-related activities.'

        if errors:
            raise ValidationError(errors)

    class Meta:
        db_table = 'deqar_country_qa_requirements'
        verbose_name = 'Country QA Requirement'
        ordering = ('id',)
        indexes = [
            models.Index(fields=['requirement_valid_to']),
        ]


class CountryInstitutionType(models.Model):
    """
    National institutional categories of HE institutions in a country, aggregated from ETER (BAS.INSTCAT).
    """
    ETER_CATEGORY_STANDARD_CHOICES = (
        (0, 'other'),
        (1, 'university'),
        (2, 'university of applied sciences'),
    )

    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', related_name='institution_types', on_delete=models.CASCADE)
    name_national = models.CharField(max_length=250)
    name_english = models.CharField(max_length=250, blank=True)
    eter_category_standard = models.SmallIntegerField(choices=ETER_CATEGORY_STANDARD_CHOICES, blank=True, null=True)
    eter_institution_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name_english} ({self.name_national})' if self.name_english else self.name_national

    class Meta:
        db_table = 'deqar_country_institution_types'
        verbose_name = 'Country Institution Type'
        ordering = ('country', 'name_national')
        constraints = [
            UniqueConstraint(fields=['country', 'name_national'],
                             name='country_institution_type_unique')
        ]


class CountryQAARegulation(models.Model):
    """
    Links to regulations relevant for QA in a country, either for the whole country or for a QA requirements group.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', on_delete=models.CASCADE)
    group = models.ForeignKey('countries.CountryQARequirementGroup', related_name='regulations',
                              on_delete=models.CASCADE, blank=True, null=True,
                              help_text='QA requirements group the regulation applies to; empty for general links')
    regulation = models.CharField(max_length=500, blank=True)
    regulation_url = models.URLField(max_length=500, blank=True)
    regulation_valid_from = models.DateField(default=datetime.date.today)
    regulation_valid_to = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.group_id is not None:
            self.country_id = self.group.country_id
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'deqar_country_qaa_regulations'
        verbose_name = 'Country QAA Regulation'
        indexes = [
            models.Index(fields=['regulation_valid_to']),
        ]


class CountryIncomingTneRegulation(models.Model):
    """
    Rules for incoming transnational education (TNE), depending on the country of origin of the foreign HEI.
    """
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey('countries.Country', related_name='incoming_tne_regulations',
                                on_delete=models.CASCADE)
    origin_groups = models.ManyToManyField('lists.TneOriginGroup', blank=True, related_name='+',
                                           verbose_name='origin country groups')
    incoming_tne_possible = models.ForeignKey('lists.TnePossible', related_name='+', on_delete=models.PROTECT,
                                              verbose_name='incoming TNE possible',
                                              help_text='whether foreign HEIs can offer TNE in the country')
    incoming_tne_conditions = models.TextField(blank=True, verbose_name='incoming TNE conditions')
    incoming_tne_approval = models.ManyToManyField('lists.TneApprovalIncoming', blank=True, related_name='+',
                                                   verbose_name='incoming TNE approval needed')
    incoming_tne_qa = models.ForeignKey('lists.TneQaIncoming', related_name='+', on_delete=models.PROTECT,
                                        verbose_name='incoming TNE QA regime')

    def __str__(self):
        if self.pk:
            groups = ', '.join(str(g) for g in self.origin_groups.all())
            if groups:
                return groups
        return f'Incoming TNE regulation #{self.pk}'

    class Meta:
        db_table = 'deqar_country_incoming_tne_regulations'
        verbose_name = 'Country Incoming TNE Regulation'
        ordering = ('id',)


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

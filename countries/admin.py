from django import forms
from django.db import models

from countries.models import Country, CountryQAARegulation, CountryQARequirement, CountryInstitutionType, \
    CountryQARequirementGroup, CountryIncomingTneRegulation
from eqar_backend.admin import admin_site, DEQARNestedModelAdmin, DEQARNestedStackedInline, \
    DEQARNestedTabularInline


def get_parent_country_id(request):
    """
    Returns the ID of the country being edited in the admin, or None when adding a new country.
    """
    if request.resolver_match:
        return request.resolver_match.kwargs.get('object_id')
    return None


class CountryQAARegulationGroupInline(DEQARNestedTabularInline):
    model = CountryQAARegulation
    fk_name = 'group'
    extra = 0
    fields = ('regulation', 'regulation_url', 'regulation_valid_from', 'regulation_valid_to')
    verbose_name = 'Regulation'
    verbose_name_plural = 'Regulations'


class CountryQARequirementForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        activity_group = cleaned_data.get('activity_group')
        if activity_group and \
                activity_group.activity_type_id == CountryQARequirement.INSTITUTIONAL_ACTIVITY_TYPE_ID and \
                cleaned_data.get('qf_ehea_levels'):
            self.add_error('qf_ehea_levels', 'QF-EHEA levels only apply to programme-related activities.')
        return cleaned_data


class CountryQARequirementInline(DEQARNestedStackedInline):
    model = CountryQARequirement
    form = CountryQARequirementForm
    extra = 0
    autocomplete_fields = ('activity_group',)
    fieldsets = (
        (None, {
            'fields': ('activity_group', 'duration', 'initial_only', 'qa_requirement_note',
                       ('requirement_valid_from', 'requirement_valid_to'))
        }),
        ('Programme scope', {
            'description': 'only applicable if the activity is not purely institutional',
            'fields': ('fields_of_education', 'qf_ehea_levels', ('full_degrees', 'micro_credentials'))
        }),
        ('Cross-border QA', {
            'description': 'criteria and recognition are only needed if cross-border QA is possible',
            'fields': ('cbqa_possible', 'cbqa_approval', 'cbqa_requirements', 'cbqa_other_requirements_note',
                       'cbqa_criteria', 'cbqa_recognition')
        }),
        ('European Approach', {
            'description': 'only applicable if the activity is not purely institutional',
            'fields': ('ea_possible', 'ea_note')
        }),
    )
    verbose_name = 'QA Requirement'
    verbose_name_plural = 'QA Requirements'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # the Select widget from formfield_overrides would otherwise replace the autocomplete widget
        if db_field.name in self.autocomplete_fields:
            kwargs.pop('widget', None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CountryQARequirementGroupForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        # legacy groups may still lack institution types, new ones need at least one
        if not self.instance.pk and not cleaned_data.get('institution_types'):
            self.add_error('institution_types', 'Select at least one institution type.')
        return cleaned_data


class CountryQARequirementGroupInline(DEQARNestedStackedInline):
    model = CountryQARequirementGroup
    form = CountryQARequirementGroupForm
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('institution_types', 'combination_logic')
        }),
        ('Outgoing TNE', {
            'fields': ('outgoing_tne_possible', 'outgoing_tne_conditions', 'outgoing_tne_approval',
                       'outgoing_tne_qa')
        }),
        ('Micro-credentials', {
            'fields': ('mc_possible', 'mc_credit_limit', 'mc_qa', 'mc_qa_note')
        }),
    )
    inlines = [CountryQARequirementInline, CountryQAARegulationGroupInline]
    verbose_name = 'QA Requirements Group'
    verbose_name_plural = 'QA Requirements Groups'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'institution_types':
            kwargs['queryset'] = CountryInstitutionType.objects.filter(country_id=get_parent_country_id(request))
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class CountryQAARegulationInline(DEQARNestedTabularInline):
    model = CountryQAARegulation
    fk_name = 'country'
    extra = 1
    fields = ('regulation', 'regulation_url', 'regulation_valid_from', 'regulation_valid_to', 'group')
    verbose_name = 'General Regulation/Link'
    verbose_name_plural = 'General Regulations/Links (select a group to move a link to a QA requirements group)'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(group__isnull=True)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'group':
            kwargs['queryset'] = CountryQARequirementGroup.objects.filter(country_id=get_parent_country_id(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CountryIncomingTneRegulationForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('origin_groups'):
            self.add_error('origin_groups', 'Select at least one origin country group.')
        return cleaned_data


class CountryIncomingTneRegulationInline(DEQARNestedStackedInline):
    model = CountryIncomingTneRegulation
    form = CountryIncomingTneRegulationForm
    extra = 0
    fields = ('origin_groups', 'incoming_tne_possible', 'incoming_tne_conditions', 'incoming_tne_approval',
              'incoming_tne_qa')
    verbose_name = 'Incoming TNE Regulation'
    verbose_name_plural = 'Incoming TNE Regulations'


class CountryInstitutionTypeInline(DEQARNestedStackedInline):
    model = CountryInstitutionType
    extra = 0
    fields = ('name_national', 'name_english', 'eter_category_standard', 'is_active')
    readonly_fields = ('name_national', 'name_english', 'eter_category_standard', 'is_active')
    verbose_name = 'Institution Type'
    verbose_name_plural = 'Institution Types (from ETER)'

    def has_add_permission(self, request, parent):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CountryAdmin(DEQARNestedModelAdmin):
    list_display = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'orgreg_eu_2_letter_code',
                    'eu_controlled_vocab_country')
    list_display_links = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
    search_fields = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
    ordering = ('name_english',)

    # identifiers can be set on create, but are immutable afterwards
    IMMUTABLE_FIELDS = ('parent', 'iso_3166_alpha2', 'iso_3166_alpha3', 'orgreg_eu_2_letter_code',
                        'orgreg_subcountry_label', 'eu_controlled_vocab_country', 'eu_controlled_vocab_atu',
                        'generic_url')
    readonly_fields = ('created_at', 'created_by')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name_english', 'parent', 'has_full_institution_list', 'general_note')
        }),
        ('Identifiers', {
            'fields': ('iso_3166_alpha2', 'iso_3166_alpha3', 'orgreg_eu_2_letter_code', 'orgreg_subcountry_label',
                       'eu_controlled_vocab_country', 'eu_controlled_vocab_atu', 'generic_url')
        }),
        ('Membership & EHEA Frameworks', {
            'fields': ('ehea_is_member', 'eqar_governmental_member_start',
                       'lrc_signatory_date', 'qf_ehea_alignment_date', 'eqf_alignment_date')
        }),
        ('QA Commitments Indicators', {
            'fields': ('ehea_key_commitment', 'external_QAA_is_permitted', 'european_approach_is_permitted', 'qa_requirement_note')
        }),
        ('Internal', {
            'fields': ('internal_note', 'created_at', 'created_by', 'flag', 'flag_log')
        }),
    )
    inlines = [CountryQARequirementGroupInline, CountryIncomingTneRegulationInline, CountryQAARegulationInline,
               CountryInstitutionTypeInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is not None:
            return tuple(readonly_fields) + self.IMMUTABLE_FIELDS
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(Country, CountryAdmin)

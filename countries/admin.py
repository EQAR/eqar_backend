from django.forms import ModelForm

from countries.models import Country, CountryQAARegulation, CountryQARequirement, CountryInstitutionType
from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline


class CountryQAARegulationInline(DEQARStackedInline):
    model = CountryQAARegulation
    extra = 1
    verbose_name = 'QAA Regulation'
    verbose_name_plural = 'QAA Regulations'


class CountryQARequirementInline(DEQARStackedInline):
    model = CountryQARequirement
    extra = 1
    verbose_name = 'QA Requirement'
    verbose_name_plural = 'QA Requirements'


class CountryInstitutionTypeInline(DEQARStackedInline):
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


class CountryAdmin(DEQARModelAdmin):
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
            'fields': ('name_english', 'parent')
        }),
        ('Identifiers', {
            'fields': ('iso_3166_alpha2', 'iso_3166_alpha3', 'orgreg_eu_2_letter_code', 'orgreg_subcountry_label',
                       'eu_controlled_vocab_country', 'eu_controlled_vocab_atu', 'generic_url')
        }),
        ('Membership', {
            'fields': ('ehea_is_member', 'eqar_governmental_member_start')
        }),
        ('Quality Assurance', {
            'fields': ('qa_requirement_note', 'external_QAA_is_permitted',
                       'eligibility', 'conditions', 'recognition', 'external_QAA_note',
                       'has_full_institution_list', 'ehea_key_commitment',
                       'european_approach_is_permitted', 'european_approach_note', 'general_note')
        }),
        ('Flag', {
            'fields': ('flag', 'flag_log')
        }),
        ('Internal', {
            'fields': ('internal_note', 'created_at', 'created_by')
        }),
    )
    inlines = [CountryQAARegulationInline, CountryQARequirementInline, CountryInstitutionTypeInline]

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

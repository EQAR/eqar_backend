from django.forms import ModelForm
from suit_ckeditor.widgets import CKEditorWidget

from countries.models import Country, CountryQAARegulation, CountryQARequirement, CountryHistoricalData
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


class CountryForm(ModelForm):
    class Meta:
        _ck_editor_toolbar = [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'documents', 'groups': ['mode']}
        ]

        _ck_editor_config = {'autoGrow_onStartup': True,
                             'autoGrow_minHeight': 100,
                             'autoGrow_maxHeight': 250,
                             'extraPlugins': 'autogrow',
                             'toolbarGroups': _ck_editor_toolbar}

        widgets = {
            'qa_requirement_note': CKEditorWidget(editor_options=_ck_editor_config),
            'eligibility': CKEditorWidget(editor_options=_ck_editor_config),
            'external_QAA_note': CKEditorWidget(editor_options=_ck_editor_config),
            'european_approach_note': CKEditorWidget(editor_options=_ck_editor_config),
            'general_note': CKEditorWidget(editor_options=_ck_editor_config),
            'recognition': CKEditorWidget(editor_options=_ck_editor_config)
        }


class CountryHistoricalDataInline(DEQARStackedInline):
    model = CountryHistoricalData
    extra = 1
    verbose_name = 'History'
    verbose_name_plural = 'Historical Entries'


class CountryAdmin(DEQARModelAdmin):
    form = CountryForm
    list_display = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'eu_controlled_vocab_country')
    list_display_links = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
    ordering = ('name_english',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
        }),
        ('Membership', {
            'fields': ('ehea_is_member', 'eqar_governmental_member_start')
        }),
        ('Quality Assurance', {
            'fields': ('qa_requirement_note', 'external_QAA_is_permitted',
                       'eligibility', 'conditions', 'recognition', 'external_QAA_note',
                       'has_full_institution_list', 'ehea_key_commitment',
                       'european_approach_is_permitted', 'european_approach_note', 'general_note')
        })
    )
    inlines = [CountryQAARegulationInline, CountryQARequirementInline, CountryHistoricalDataInline]

admin_site.register(Country, CountryAdmin)

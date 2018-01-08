from django.contrib.admin import ModelAdmin, StackedInline
from django.db import models
from django.forms import TextInput, Textarea, ModelForm
from suit_ckeditor.widgets import CKEditorWidget

from countries.models import Country, CountryQAARegulation
from eqar_backend.admin import admin_site, DEQARModelAdmin


class CountryQAARegulationInline(StackedInline):
    model = CountryQAARegulation
    extra = 1
    verbose_name = 'QAA Regulation'
    verbose_name_plural = 'QAA Regulations'
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span8'})},
    }


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
            'qa_requirement_notes': CKEditorWidget(editor_options=_ck_editor_config),
            'eligibility': CKEditorWidget(editor_options=_ck_editor_config),
            'external_QAA_permitted_note': CKEditorWidget(editor_options=_ck_editor_config),
            'european_approach_note': CKEditorWidget(editor_options=_ck_editor_config),
            'general_note': CKEditorWidget(editor_options=_ck_editor_config)
        }


class CountryAdmin(DEQARModelAdmin):
    form = CountryForm
    list_display = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
    list_display_links = ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
    ordering = ('name_english',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name_english', 'iso_3166_alpha2', 'iso_3166_alpha3')
        }),
        ('Membership', {
            'fields': ('ehea_is_member', 'eqar_govermental_member_start')
        }),
        ('Quality Assurance', {
            'fields': ('qa_requirement', 'qa_requirement_type', 'qa_requirement_notes', 'external_QAA_is_permitted',
                       'eligibility', 'conditions', 'recognition', 'external_QAA_permitted_note',
                       'european_approach_is_permitted', 'european_approach_note', 'general_note')
        })
    )
    inlines = [CountryQAARegulationInline]

admin_site.register(Country, CountryAdmin)

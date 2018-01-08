from django.contrib.admin import StackedInline, ModelAdmin, TabularInline
from django.forms import TextInput, Textarea, ModelForm, URLInput, ModelChoiceField
from suit_ckeditor.widgets import CKEditorWidget

from agencies.models import *
from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline, DEQARTabularInline


class AgencyFocusCountriesInline(DEQARTabularInline):
    model = AgencyFocusCountry
    extra = 1
    suit_classes = 'suit-tab suit-tab-focus_countries'
    verbose_name = 'Focus Country'
    verbose_name_plural = 'Focus Countries'


class AgencyPhonesInline(DEQARStackedInline):
    model = AgencyPhone
    extra = 1
    suit_classes = 'suit-tab suit-tab-contact'
    verbose_name = 'Phone Number'
    verbose_name_plural = 'Phone Numbers'


class AgencyEmailsInline(DEQARStackedInline):
    model = AgencyEmail
    extra = 1
    suit_classes = 'suit-tab suit-tab-contact'
    verbose_name = 'E-mail'
    verbose_name_plural = 'E-mails'


class AgencyMembershipsInline(DEQARStackedInline):
    model = AgencyMembership
    extra = 1
    suit_classes = 'suit-tab suit-tab-other'
    verbose_name = 'Membership'
    verbose_name_plural = 'Memberships'


class AgencyESGActivityInline(DEQARStackedInline):
    model = AgencyESGActivity
    extra = 0
    suit_classes = 'suit-tab suit-tab-esg'
    verbose_name = 'ESG Activity'
    verbose_name_plural = 'ESG Activities'


class AgencyEQARDecisionInline(DEQARStackedInline):
    model = AgencyEQARDecision
    extra = 1
    suit_classes = 'suit-tab suit-tab-decision'
    verbose_name = 'Decision'
    verbose_name_plural = 'Decisions'


class AgencyForm(ModelForm):
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
            'address': CKEditorWidget(editor_options=_ck_editor_config),
            'specialisation_note': CKEditorWidget(editor_options=_ck_editor_config),
            'description_note': CKEditorWidget(editor_options=_ck_editor_config),
            'registration_note': CKEditorWidget(editor_options=_ck_editor_config)
        }


class AgencyAdmin(DEQARModelAdmin):
    form = AgencyForm
    list_display = ('acronym_primary', 'name_primary')
    list_display_links = ('acronym_primary', 'name_primary')
    list_filter = ('country',)
    date_hierarchy = 'registration_start'

    suit_form_tabs = (('name', 'Name'),
                      ('focus_countries', 'Focus Countries'),
                      ('contact', 'Contact Information'),
                      ('other', 'Other Information'),
                      ('esg', 'ESG Activities'),
                      ('decision', 'EQAR Decision'),
                      )
    fieldsets = (
        (None, {
            'fields': ('deqar_id', 'acronym_primary', 'name_primary'),
            'classes': ('suit-tab', 'suit-tab-name',)

        }),
        (None, {
            'fields': ('contact_person', 'website_link', 'logo', 'fax', 'address', 'country'),
            'classes': ('suit-tab', 'suit-tab-contact',),
        }),
        (None, {
            'fields': ('reports_link', 'geographical_focus', 'specialisation_note', 'description_note', 'registration_start',
                       'registration_valid_to', 'registration_note'),
            'classes': ('suit-tab', 'suit-tab-other',),
        })
    )
    inlines = [AgencyPhonesInline, AgencyEmailsInline, AgencyFocusCountriesInline, AgencyMembershipsInline,
               AgencyEQARDecisionInline, AgencyESGActivityInline]


class AgencyNameVersionInline(DEQARStackedInline):
    model = AgencyNameVersion
    extra = 0
    verbose_name = 'Name Version'
    verbose_name_plural = 'Name Versions'


class AgencyNameAdmin(DEQARModelAdmin):
    list_display = ('agency', 'valid_to')
    ordering = ('agency',)
    list_filter = ('agency',)
    inlines = (AgencyNameVersionInline,)


admin_site.register(Agency, AgencyAdmin)
admin_site.register(AgencyName, AgencyNameAdmin)
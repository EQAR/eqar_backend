from django import forms
from django.db.models import Count
from django.db.models.functions import Lower
from django.forms import CharField, TextInput, Textarea

from agencies.models import *
from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline, DEQARTabularInline
from django.utils.html import format_html

class AgencyProxyInline(DEQARStackedInline):
    model = AgencyProxy
    extra = 1
    verbose_name = 'Agency Proxy'
    verbose_name_plural = 'Agency Proxies'

class SubmittingAgencyAdmin(DEQARModelAdmin):
    list_display = ('agency', 'external_agency')
    list_display_links = ('agency', 'external_agency')
    fields = ['agency', 'external_agency', 'external_agency_acronym', 'registration_from', 'registration_to']
    inlines = [AgencyProxyInline]

class AgencyESGActivityAdmin(DEQARModelAdmin):
    list_display = ('id', '_agency', '_activity_group')
    list_display_links = ('id', '_agency', '_activity_group')
    fields = ['agency', 'activity_group', 'activity_local_identifier', 'activity_description',
              'reports_link', 'activity_valid_from', 'activity_valid_to']
    list_filter = ('agency',)

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        models.URLField: {'widget': TextInput(attrs={'size': '80'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    def _activity_group(self, obj):
        return format_html(
            f'<div style="width: 90%; word-wrap: break-word">{obj.activity_group}</div>'
        )

    def _agency(self, obj):
        return obj.agency.acronym_primary

class AgencyActivityGroupAdmin(DEQARModelAdmin):
    list_display = ('id', 'activity', 'assigned_agencies', 'assigned_agencies_list')
    list_display_links = ('id', 'activity', 'assigned_agencies')
    fields = ['activity', 'activity_type', 'reports_link']
    ordering = (Lower('activity'),)

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '80'})},
        models.URLField: {'widget': TextInput(attrs={'size': '80'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    def assigned_agencies(self, obj):
        return obj._assigned_agencies

    def assigned_agencies_list(self, obj):
        agencies = set()
        for agency in obj.agencyesgactivity_set.all():
            agencies.add(agency.agency.acronym_primary)
        agencies = sorted(agencies, key=str.lower)
        return ', '.join(agencies)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_assigned_agencies=Count("agencyesgactivity__agency", distinct=True))
        return queryset

    assigned_agencies.admin_order_field = '_assigned_agencies'

admin_site.register(SubmittingAgency, SubmittingAgencyAdmin)
admin_site.register(AgencyESGActivity, AgencyESGActivityAdmin)
admin_site.register(AgencyActivityGroup, AgencyActivityGroupAdmin)
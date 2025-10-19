from django.contrib.admin import TabularInline, StackedInline, display
from django.db import models
from django.forms import TextInput, Textarea, Select
from django.utils.html import format_html
from django.conf import settings

from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline
from institutions.models import Institution, InstitutionIdentifier, InstitutionQFEHEALevel, \
    InstitutionName, InstitutionNameVersion, InstitutionCountry, InstitutionHistoricalData, \
    InstitutionHistoricalRelationship, InstitutionHierarchicalRelationship, InstitutionUpdateLog, InstitutionFlag


class InstitutionIdentifierInline(TabularInline):
    model = InstitutionIdentifier
    verbose_name = 'Identifier'
    verbose_name_plural = 'Identifiers'
    fields = ('identifier', 'resource', 'agency')


class InstitutionCountryInline(TabularInline):
    model = InstitutionCountry
    verbose_name = 'Country'
    verbose_name_plural = 'Countries'
    fields = ('country_verified', 'country', 'city', 'lat', 'long')


class InstitutionNameInline(TabularInline):
    model = InstitutionName
    verbose_name = 'Name'
    verbose_name_plural = 'Names'
    fields = ('name_official', 'name_english', 'name_valid_to')
    ordering = ('-name_valid_to',)


class InstitutionHistoricalSourceInline(TabularInline):
    model = InstitutionHistoricalRelationship
    fields = ('relationship_type', 'institution_source', 'relationship_note', 'relationship_date')
    fk_name = 'institution_target'
    verbose_name = 'Historical relationship (=>)'
    verbose_name_plural = 'Historical relationships (=>)'

class InstitutionHistoricalTargetInline(TabularInline):
    model = InstitutionHistoricalRelationship
    fields = ('relationship_type', 'institution_target', 'relationship_note', 'relationship_date')
    fk_name = 'institution_source'
    verbose_name = 'Historical relationship (<=)'
    verbose_name_plural = 'Historical relationships (<=)'


class ParentInstitutionInline(TabularInline):
    model = InstitutionHierarchicalRelationship
    fields = ('institution_parent', 'relationship_type', 'relationship_note', 'valid_from', 'valid_to',)
    fk_name = 'institution_child'
    verbose_name = 'Part of'
    verbose_name_plural = 'Part of'

class ChildInstitutionInline(TabularInline):
    model = InstitutionHierarchicalRelationship
    fields = ('institution_child', 'relationship_type', 'relationship_note', 'valid_from', 'valid_to',)
    fk_name = 'institution_parent'
    verbose_name = 'Includes'
    verbose_name_plural = 'Includes'


class InstitutionUpdateLogInline(TabularInline):
    model = InstitutionUpdateLog
    ordering = ('-updated_at',)


class InstitutionAdmin(DEQARModelAdmin):
    list_display = ('deqar_id', 'eter_id', 'name_primary', 'website_link', 'is_other_provider')
    list_display_links = ('name_primary',)
    ordering = ('name_primary',)
    search_fields = ('name_primary', 'website_link')

    fieldsets = (
        ('Basic Information', {
            'fields': ('deqar_id', 'eter_id_link', 'name_primary', 'website_link', 'is_other_provider', 'founding_date', 'closure_date')
        }),
        ('Reports', {
            'fields': ('report_count', 'platform_count',)
        }),
    )

    inlines = [
        InstitutionNameInline,
        InstitutionIdentifierInline,
        InstitutionCountryInline,
        InstitutionHistoricalSourceInline,
        InstitutionHistoricalTargetInline,
        ParentInstitutionInline,
        ChildInstitutionInline,
        InstitutionUpdateLogInline,
    ]

    @display(description="OrgReg/ETER ID")
    def eter_id_link(self, obj):
        if obj.eter_id:
            return format_html('<a href="https://register.orgreg.joanneum.at/#/entity-details/{eter_id}">{eter_id}</a>', eter_id=obj.eter_id)
        else:
            return '-'

    @display(description="As provider")
    def report_count(self, obj):
        return obj.reports.count()

    @display(description="As platform")
    def platform_count(self, obj):
        return obj.related_reports.count()

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        else:
            if obj.reports.count() + obj.related_reports.count() > 0:
                return False
            else:
                return True

    def view_on_site(self, obj):
        if hasattr(settings, 'DEQAR_INSTITUTION_URI'):
            return settings.DEQAR_INSTITUTION_URI % obj.pk
        else:
            return False

admin_site.register(Institution, InstitutionAdmin)


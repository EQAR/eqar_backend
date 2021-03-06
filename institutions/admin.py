from django.contrib.admin import StackedInline
from django.db import models
from django.forms import TextInput, Textarea, Select

from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline
from institutions.models import Institution, InstitutionIdentifier, InstitutionQFEHEALevel, \
    InstitutionETERRecord, InstitutionName, InstitutionNameVersion, InstitutionCountry, InstitutionHistoricalData, \
    InstitutionHistoricalRelationship, InstitutionHierarchicalRelationship, InstitutionUpdateLog, InstitutionFlag


class InstitutionIdentifierInline(StackedInline):
    model = InstitutionIdentifier
    extra = 1
    verbose_name = 'Identifier'
    verbose_name_plural = 'Identifiers'


class InstitutionQFEHEALevelInline(StackedInline):
    model = InstitutionQFEHEALevel
    extra = 1
    verbose_name = 'QF-EHEA level'
    verbose_name_plural = 'QF-EHEA levels'


class InstitutionCountryInline(StackedInline):
    model = InstitutionCountry
    extra = 1
    verbose_name = 'Country'
    verbose_name_plural = 'Countries'


class InstitutionHistoricalDataInline(DEQARStackedInline):
    model = InstitutionHistoricalData
    extra = 1
    verbose_name = 'History'
    verbose_name_plural = 'Historical Entries'


class InstitutionAdmin(DEQARModelAdmin):
    list_display = ('name_primary', 'website_link')
    list_display_links = ('name_primary',)
    ordering = ('name_primary',)
    search_fields = ('name_primary', 'website_link')

    fieldsets = (
        ('Basic Information', {
            'fields': ('deqar_id', 'eter', 'name_primary', 'website_link', 'founding_date', 'closure_date')
        }),
    )

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span10'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'span10', 'rows': 4})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span10'})},
        models.ForeignKey: {'widget': Select(attrs={'class': 'span10'})},
    }

    inlines = [InstitutionIdentifierInline, InstitutionQFEHEALevelInline,
               InstitutionCountryInline, InstitutionHistoricalDataInline]


class InstitutionETERAdmin(DEQARModelAdmin):
    list_display = ('eter_id', 'name', 'acronym')
    list_display_links = ('eter_id', 'name', 'acronym')
    ordering = ('name', 'acronym')
    list_filter = ('country',)
    search_fields = ('name', 'name_english', 'acronym')


class InstitutionNameVersionInline(DEQARStackedInline):
    model = InstitutionNameVersion
    extra = 0
    verbose_name = 'Name Version'
    verbose_name_plural = 'Name Versions'


class InstitutionNameAdmin(DEQARModelAdmin):
    list_display = ('institution', 'name_official', 'name_valid_to')
    ordering = ('institution', 'name_official',)
    list_filter = ('institution',)
    inlines = (InstitutionNameVersionInline, )


class InstitutionHistoricalRelationshipAdmin(DEQARModelAdmin):
    fields = ('institution_source', 'relationship_type', 'institution_target', 'relationship_note', 'relationship_date')
    list_display = ('institution_source', 'relationship_type', 'institution_target')
    ordering = ('institution_source', 'institution_target')
    list_filter = ('institution_source', 'institution_target')


class InstitutionHierarchicalRelationshipAdmin(DEQARModelAdmin):
    list_display = ('institution_parent', 'institution_child', 'relationship_type')
    ordering = ('institution_parent', 'institution_child')
    list_filter = ('institution_parent', 'institution_child', 'relationship_type')


class InstitutionFlagAdmin(DEQARModelAdmin):
    list_display = ('institution', 'flag', 'flag_message', 'active', 'removed_by_eqar')
    ordering = ('institution', 'flag', 'active')
    list_filter = ('institution', 'flag', 'active', 'removed_by_eqar')


class InstitutionUpdateLogAdmin(DEQARModelAdmin):
    list_display = ('institution', 'updated_at', 'updated_by')
    ordering = ('institution',)
    list_filter = ('institution',)


admin_site.register(InstitutionName, InstitutionNameAdmin)
admin_site.register(Institution, InstitutionAdmin)
admin_site.register(InstitutionETERRecord, InstitutionETERAdmin)
admin_site.register(InstitutionHistoricalRelationship, InstitutionHistoricalRelationshipAdmin)
admin_site.register(InstitutionHierarchicalRelationship, InstitutionHierarchicalRelationshipAdmin)
admin_site.register(InstitutionFlag, InstitutionFlagAdmin)
admin_site.register(InstitutionUpdateLog, InstitutionUpdateLogAdmin)


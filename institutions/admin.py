from django.contrib.admin import StackedInline
from django.db import models
from django.forms import TextInput, Textarea, Select

from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline
from institutions.models import Institution, InstitutionIdentifier, InstitutionCountry, InstitutionQFEHEALevel, \
    InstitutionETERRecord, InstitutionName, InstitutionNameVersion


class InstitutionIdentifierInline(StackedInline):
    model = InstitutionIdentifier
    extra = 1
    verbose_name = 'Identifier'
    verbose_name_plural = 'Identifiers'


class InstitutionCountryInline(StackedInline):
    model = InstitutionCountry
    extra = 1
    verbose_name = 'Country'
    verbose_name_plural = 'Countries'


class InstitutionQFEHEALevelInline(StackedInline):
    model = InstitutionQFEHEALevel
    extra = 1
    verbose_name = 'QF-EHEA level'
    verbose_name_plural = 'QF-EHEA levels'


class InstitutionAdmin(DEQARModelAdmin):
    list_display = ('name_primary', 'website_link')
    list_display_links = ('name_primary',)
    ordering = ('name_primary',)
    search_fields = ('institutionname_set__name_official', 'institutionname_set__name_english',
                     'institutionname_set__acronym')

    fieldsets = (
        ('Basic Information', {
            'fields': ('deqar_id', 'eter', 'name_primary', 'website_link')
        }),
    )

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span10'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'span10', 'rows': 4})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span10'})},
        models.ForeignKey: {'widget': Select(attrs={'class': 'span10'})},
    }

    inlines = [InstitutionIdentifierInline, InstitutionCountryInline, InstitutionQFEHEALevelInline]


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
    list_display = ('institution', 'name_official', 'valid_to')
    ordering = ('institution', 'name_official',)
    list_filter = ('institution',)
    inlines = (InstitutionNameVersionInline,)


admin_site.register(InstitutionName, InstitutionNameAdmin)
admin_site.register(Institution, InstitutionAdmin)
admin_site.register(InstitutionETERRecord, InstitutionETERAdmin)

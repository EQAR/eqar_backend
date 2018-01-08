from eqar_backend.admin import DEQARModelAdmin, admin_site, DEQARStackedInline
from programmes.models import Programme
from reports.models import Report, ReportFile


class ReportProgrammeInline(DEQARStackedInline):
    model = Programme
    fk_name = 'report'
    extra = 1
    suit_classes = 'suit-tab suit-tab-programme'
    verbose_name = 'Programme'
    verbose_name_plural = 'Programmes'
    filter_horizontal = ('countries',)


class ReportFileInline(DEQARStackedInline):
    model = ReportFile
    extra = 1
    suit_classes = 'suit-tab suit-tab-file'
    verbose_name = 'File'
    verbose_name_plural = 'Files'
    filter_horizontal = ('languages',)


class ReportAdmin(DEQARModelAdmin):
    list_display = ('get_agency_acronym', 'name')
    list_display_links = ('get_agency_acronym', 'name')
    ordering = ('agency', 'name')
    list_filter = ('agency',)
    filter_horizontal = ('institutions',)

    suit_form_tabs = (('report', 'Report'),
                      ('institution', 'Institutions'),
                      ('programme', 'Programmes'),
                      ('file', 'Files'))
    fieldsets = (
        (None, {
            'fields': ('agency', 'agency_esg_activity', 'local_identifier', 'name', 'status', 'decision',
                       'valid_from', 'valid_to'),
            'classes': ('suit-tab', 'suit-tab-report',)
        }),
        (None, {
            'fields': ('institutions',),
            'classes': ('suit-tab', 'suit-tab-institution')
        })
    )
    inlines = [ReportFileInline, ReportProgrammeInline]

    def get_agency_acronym(self, obj):
        return obj.agency.acronym_primary
    get_agency_acronym.short_description = 'Agency'

admin_site.register(Report, ReportAdmin)

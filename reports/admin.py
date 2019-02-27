from eqar_backend.admin import DEQARModelAdmin, admin_site, DEQARStackedInline
from programmes.models import Programme
from reports.models import Report, ReportFile, ReportLink


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


class ReportLinkInline(DEQARStackedInline):
    model = ReportLink
    extra = 1
    suit_classes = 'suit-tab suit-tab-report'
    verbose_name = 'Link'
    verbose_name_plural = 'Links'


class ReportAdmin(DEQARModelAdmin):
    list_display = ('id', 'local_identifier', 'agency_esg_activity', 'get_institutions', 'get_programme')
    list_display_links = ('id', 'agency_esg_activity')
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
                       'valid_from', 'valid_to', 'flag'),
            'classes': ('suit-tab', 'suit-tab-report',)
        }),
        (None, {
            'fields': ('institutions',),
            'classes': ('suit-tab', 'suit-tab-institution')
        })
    )
    inlines = [ReportFileInline, ReportProgrammeInline, ReportLinkInline]

    def get_institutions(self, obj):
        return ", ".join(str(inst) for inst in obj.institutions.all())
    get_institutions.short_description = 'Institution(s)'

    def get_programme(self, obj):
        return ", ".join(prg.name_primary for prg in obj.programme_set.all())
    get_programme.short_description = 'Programme(s)'

admin_site.register(Report, ReportAdmin)

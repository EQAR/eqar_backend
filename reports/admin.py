from eqar_backend.admin import DEQARModelAdmin, admin_site, DEQARStackedInline
from programmes.models import Programme
from reports.models import Report, ReportFile, ReportLink, ReportUpdateLog, ReportFlag
from submissionapi.models import SubmissionReportLog


class ReportProgrammeInline(DEQARStackedInline):
    model = Programme
    fk_name = 'report'
    verbose_name = 'Programme'
    verbose_name_plural = 'Programmes'


class ReportFileInline(DEQARStackedInline):
    model = ReportFile
    verbose_name = 'File'
    verbose_name_plural = 'Files'


class ReportLinkInline(DEQARStackedInline):
    model = ReportLink
    verbose_name = 'Link'
    verbose_name_plural = 'Links'


class SubmissionReportLogInline(DEQARStackedInline):
    model = SubmissionReportLog
    verbose_name = 'Submission log'
    verbose_name_plural = 'Submission logs'
    fields = ('submission_package_log',)


class ReportUpdateLogInline(DEQARStackedInline):
    model = ReportUpdateLog
    verbose_name = 'Update log'
    verbose_name_plural = 'Update logs'
    readonly_fields = ('updated_at',)


class ReportFlagInline(DEQARStackedInline):
    model = ReportFlag
    verbose_name = 'Flag'
    verbose_name_plural = 'Flags'
    readonly_fields = ('created_at', 'updated_at',)


class ReportAdmin(DEQARModelAdmin):
    list_display = ('id', 'get_agencies', 'local_identifier', 'get_agency_esg_activities', 'get_institutions', 'get_programme', 'flag')
    ordering = ('-id',)
    list_filter = ('agency_esg_activities__activity_group__activity_type', 'flag', 'agency', 'agency_esg_activities__activity_group__activity')

    inlines = [ReportFileInline, ReportProgrammeInline, ReportLinkInline, ReportFlagInline, SubmissionReportLogInline, ReportUpdateLogInline ]

    def get_agencies(self, obj):
        agency = obj.agency.acronym_primary
        if obj.contributing_agencies.count():
            agency += " (+ " + ", ".join(a.acronym_primary for a in obj.contributing_agencies.all()) + ")"
        return agency
    get_agencies.short_description = 'Agency(-ies)'

    def get_agency_esg_activities(self, obj):
        return ", ".join(activity.activity_group.activity for activity in obj.agency_esg_activities.all())
    get_agency_esg_activities.short_description = 'Activity(-ies)'

    def get_institutions(self, obj):
        return ", ".join(str(inst) for inst in obj.institutions.all())
    get_institutions.short_description = 'Institution(s)'

    def get_programme(self, obj):
        return ", ".join(prg.name_primary for prg in obj.programme_set.all())
    get_programme.short_description = 'Programme(s)'

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin_site.register(Report, ReportAdmin)

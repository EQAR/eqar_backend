from django.contrib import admin

# Register your models here.
from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline
from submissionapi.models import SubmissionPackageLog, SubmissionReportLog


class SubmissionReportLogInline(DEQARStackedInline):
    model = SubmissionReportLog
    fk_name = 'submission_package_log'
    extra = 1
    verbose_name = 'Reports'
    verbose_name_plural = 'Reports'


class SubmissionLogAdmin(DEQARModelAdmin):
    list_display = ('id', 'get_user', 'user_ip_address', 'origin', 'submission_date')
    list_display_links = ('id', 'get_user', 'user_ip_address')
    ordering = ('id', 'user', 'origin', 'submission_date')
    list_filter = ('user', 'origin')
    inlines = [SubmissionReportLogInline,]

    def get_user(self, obj):
        return obj.user.user.username
    get_user.short_description = 'User'


admin_site.register(SubmissionPackageLog, SubmissionLogAdmin)

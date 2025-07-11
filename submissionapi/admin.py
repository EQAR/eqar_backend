from django.contrib import admin

import json
import ast
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from django.utils.safestring import mark_safe

# Register your models here.
from eqar_backend.admin import admin_site, DEQARModelAdmin, DEQARStackedInline
from submissionapi.models import SubmissionPackageLog, SubmissionReportLog


class SubmissionReportLogInline(DEQARStackedInline):
    model = SubmissionReportLog
    fk_name = 'submission_package_log'
    verbose_name = 'Report'
    verbose_name_plural = 'Reports'
    readonly_fields = ('agency', 'report', 'report_status', 'submission_date')
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class SubmissionLogAdmin(DEQARModelAdmin):
    list_display = ('id', 'user', 'user_ip_address', 'origin', 'submission_date')
    list_display_links = ('id', 'submission_date')
    ordering = ('-id',) # 'user', 'origin', 'submission_date')
    list_filter = ('user', 'origin', 'submission_date')
    inlines = [SubmissionReportLogInline,]
    readonly_fields = ('user','origin','user_ip_address','submission_date','submitted_data_pp','submission_errors_pp')
    exclude = ('submitted_data','submission_errors')

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def submitted_data_pp(self, instance):
        # return the data as pretty-printed JSON
        if instance.origin == 'csv':
            return instance.submitted_data
        else:
            if instance.submitted_data.lstrip().startswith('{') or instance.submitted_data.lstrip().startswith('['):
                # convert dict/list repr to JSON
                content = json.dumps(ast.literal_eval(instance.submitted_data), indent=2)
                # highlight the data
                formatter = HtmlFormatter()
                response = highlight(content, JsonLexer(), formatter)
                # add the stylesheet
                style = "<style>" + formatter.get_style_defs() + "</style>\n"
                # return the output
                return mark_safe(style + response)
            else:
                return instance.submitted_data

    submitted_data_pp.short_description = 'submitted data'

    def submission_errors_pp(self, instance):
        # return the errors as pretty-printed JSON
        try:
            content = json.dumps(json.loads(instance.submission_errors), indent=2)
            # highlight the data
            formatter = HtmlFormatter()
            response = highlight(content, JsonLexer(), formatter)
            # add the stylesheet
            style = "<style>" + formatter.get_style_defs() + "</style>\n"
            # return the output
            return mark_safe(style + response)
        except ValueError:
            return instance.submission_errors

    submission_errors_pp.short_description = 'submission errors'

admin_site.register(SubmissionPackageLog, SubmissionLogAdmin)

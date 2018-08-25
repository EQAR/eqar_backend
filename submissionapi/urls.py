from django.conf.urls import url

from submissionapi.views.csv_upload_report_view import SubmissionCSVView
from submissionapi.views.report_file_upload_view import ReportFileUploadView
from submissionapi.views.submission_report_view import SubmissionReportView

app_name = 'submissionapi'

urlpatterns = [
    url(r'^submit/report$', SubmissionReportView.as_view(), name='submit-report'),
    url(r'^submit/csv', SubmissionCSVView.as_view(), name='submit-csv'),
    url(r'^submit/reportfile/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$', ReportFileUploadView.as_view(),
        name='upload-report_file')
]

from django.conf.urls import url
from submissionapi.views import Submission, ReportFileUploadView

urlpatterns = [
    url(r'^submit/report$', Submission.as_view(), name='submit-report'),
    url(r'^submit/reportfile/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$', ReportFileUploadView.as_view(),
        name='upload-report_file')
]

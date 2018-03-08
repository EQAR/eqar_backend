from django.conf.urls import url

from adminapi.views.dashboard_views import ReportsByAgency
from submissionapi.views import Submission, ReportFileUploadView

urlpatterns = [
    url(r'^reports_by_agency$', ReportsByAgency.as_view(), name='submit-report'),
]

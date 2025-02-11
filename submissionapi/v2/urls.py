from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from submissionapi.v1.views.csv_upload_report_view import SubmissionCSVView
from submissionapi.v2.views.check_local_identifier_view import CheckLocalIdentifierView
from submissionapi.v2.views.submission_report_view import SubmissionReportView, ReportDelete
from submissionapi.v2.views.submission_report_file_views import ReportFileView

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Submission API",
      default_version='v2',
      description="Documentation of the API responsible for data submission the DEQAR",
      contact=openapi.Contact(email="info@eqar.eu"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'submissionapi'

urlpatterns = [
    url(r'^submit/report$', SubmissionReportView.as_view(), name='submit-report-v2'),
    url(r'^submit/csv', SubmissionCSVView.as_view(), name='submit-csv'),

    url(r'^check/local-identifier', CheckLocalIdentifierView.as_view(), name='check-report-local-identifier'),

    url(r'^manage/report-file$', ReportFileView.as_view(), name='report_file-manage'),
    url(r'^delete/report/(?P<pk>[0-9]+)/$', ReportDelete.as_view(), name='report-delete'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

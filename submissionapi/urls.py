from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from submissionapi.views.csv_upload_report_view import SubmissionCSVView
from submissionapi.views.report_file_upload_view import ReportFileUploadView
from submissionapi.views.submission_report_view import SubmissionReportView, ReportDelete

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Submission API",
      default_version='v1',
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
    url(r'^submit/report$', SubmissionReportView.as_view(), name='submit-report'),
    url(r'^submit/csv', SubmissionCSVView.as_view(), name='submit-csv'),
    url(r'^submit/reportfile/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$', ReportFileUploadView.as_view(),
        name='upload-report_file'),
    url(r'^delete/report/(?P<pk>[0-9]+)/$', ReportDelete.as_view(), name='report-delete'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

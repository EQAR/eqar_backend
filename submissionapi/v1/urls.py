from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from submissionapi.v1.views.csv_upload_report_view import SubmissionCSVView
from submissionapi.v1.views.report_file_upload_view import ReportFileUploadView
from submissionapi.v1.views.submission_report_view import SubmissionReportView, ReportDelete

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
    re_path(r'^submit/report$', SubmissionReportView.as_view(), name='submit-report'),
    re_path(r'^submit/csv', SubmissionCSVView.as_view(), name='submit-csv'),
    re_path(r'^submit/reportfile/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$', ReportFileUploadView.as_view(),
        name='upload-report_file'),
    re_path(r'^delete/report/(?P<pk>[0-9]+)/$', ReportDelete.as_view(), name='report-delete'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

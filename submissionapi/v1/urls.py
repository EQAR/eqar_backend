from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from submissionapi.v1.views import ClosureView

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Submission API",
      default_version='v1',
      description="The Submission API v1 endpoints were closed on 2026-04-06. Please refer to the documentation for the new Submission API v2.",
      contact=openapi.Contact(email="info@eqar.eu"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'submissionapi'

urlpatterns = [
    re_path(r'^submit/report$', ClosureView.as_view(), name='submit-report'),
    re_path(r'^submit/reportfile/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$', ClosureView.as_view(),
        name='upload-report_file'),
    re_path(r'^delete/report/(?P<pk>[0-9]+)/$', ClosureView.as_view(), name='report-delete'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

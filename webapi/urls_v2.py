from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from webapi.views.institution_v2_views import *
from webapi.views.report_v2_views import *

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Web API",
      default_version='v2',
      description="API documentation of the API serving the DEQAR website",
      contact=openapi.Contact(email="info@eqar.eu"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'webapi'

urlpatterns = [
    url(r'^browse/institutions/$', InstitutionList.as_view(), name='institution-list'),

    url(r'^browse/reports/programme/by-institution/(?P<institution>[0-9]+)/$',
        ReportProgrammeListByInstitution.as_view(), name='programme-report-list-by-institution'),
    url(r'^browse/reports/institutional/by-institution/(?P<institution>[0-9]+)/$',
        ReportInstitutionListByInstitution.as_view(), name='institutional-report-list-by-institution'),


    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

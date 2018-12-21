from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from webapi.views.agency_views import *
from webapi.views.country_views import *
from webapi.views.institution_views import *
from webapi.views.report_views import *

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Web API",
      default_version='v1',
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
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),
    url(r'^browse/agencies/focusing-to/(?P<country>[0-9]+)/$', AgencyListByFocusCountry.as_view(),
        name='agency-list-by-focuscountry'),
    url(r'^browse/agencies/based-in/(?P<country>[0-9]+)/$', AgencyListByOriginCountry.as_view(),
        name='agency-list-by-country'),
    url(r'^browse/agencies/decisions/$', AgencyDecisionList.as_view(), name='agency-decision-list'),

    url(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    url(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),
    url(r'^browse/countries/by-agency-focus/(?P<agency>[0-9]+)/$', CountryListByAgency.as_view(),
        name='country-list-by-agency'),
    url(r'^browse/countries/by-reports/$', CountryListByReports.as_view(), name='country-list-by-reports'),

    url(r'^browse/institutions/$', InstitutionList.as_view(), name='institution-list'),
    url(r'^browse/institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-detail'),

    url(r'^browse/reports/programme/by-institution/(?P<institution>[0-9]+)/$',
        ReportProgrammeListByInstitution.as_view(), name='programme-report-list-by-institution'),
    url(r'^browse/reports/institutional/by-institution/(?P<institution>[0-9]+)/$',
        ReportInstitutionListByInstitution.as_view(), name='institutional-report-list-by-institution'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

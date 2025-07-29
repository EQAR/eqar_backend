from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from eqar_backend.schema_generator import HttpsSchemaGenerator
from webapi.v2.views.agency_views import AgencyList, AgencyDetail, AgencyListByFocusCountry, AgencyListByOriginCountry, \
    AgencyDecisionList, AgencyActivityList, AgencyActivityGroupList
from webapi.v2.views.country_views import CountryList, CountryDetail, CountryListByAgency, CountryListByReports
from webapi.v2.views.institution_views import *
from webapi.v2.views.report_search_views import ReportList
from webapi.v2.views.report_views import *

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
    generator_class=HttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'webapi'

urlpatterns = [
    # Agency endpoints
    re_path(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    re_path(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),
    re_path(r'^browse/agencies/focusing-to/(?P<country>[0-9]+)/$', AgencyListByFocusCountry.as_view(),
        name='agency-list-by-focuscountry'),
    re_path(r'^browse/agencies/based-in/(?P<country>[0-9]+)/$', AgencyListByOriginCountry.as_view(),
        name='agency-list-by-country'),
    re_path(r'^browse/agencies/decisions/$', AgencyDecisionList.as_view(), name='agency-decision-list'),
    re_path(r'^browse/agencies/activities/$', AgencyActivityList.as_view(), name='agency-activity-list'),
    re_path(r'^browse/agencies/activity-groups/$', AgencyActivityGroupList.as_view(), name='agency-activity-group-list'),

    # Country endpoints
    re_path(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    re_path(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),
    re_path(r'^browse/countries/by-agency-focus/(?P<agency>[0-9]+)/$', CountryListByAgency.as_view(),
        name='country-list-by-agency'),
    re_path(r'^browse/countries/by-reports/$', CountryListByReports.as_view(), name='country-list-by-reports'),

    # Institution endpoints
    re_path(r'^browse/institutions/$', InstitutionList.as_view(), name='institution-list'),
    re_path(r'^browse/institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-detail'),
    re_path(r'^browse/institutions/by-eter/(?P<eter_id>[^/]+)/$', InstitutionDetailByETER.as_view(),
        name='institution-eter_id-detail'),
    re_path(r'^browse/institutions/by-identifier/(?P<resource>[^/]+)/(?P<identifier>[^/]+)$', InstitutionDetailByIdentifier.as_view(),
        name='institution-by-identifier-detail'),
    re_path(r'^browse/institutions/resources/$', InstitutionIdentifierResourcesList.as_view(),
        name='institution-resources'),

    # Reports endpoints
    re_path(r'^browse/reports/$', ReportList.as_view(), name='report-list'),
    re_path(r'^browse/reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-detail'),
    re_path(r'^browse/reports/programme/by-institution/(?P<institution>[0-9]+)/$',
        ProgrammesByInstitution.as_view(),
        name='programme-report-list-by-institution'),
    re_path(r'^browse/reports/institutional/by-institution/(?P<institution>[0-9]+)/$',
        InstitutionalReportsByInstitution.as_view(),
        name='institutional-report-list-by-institution'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

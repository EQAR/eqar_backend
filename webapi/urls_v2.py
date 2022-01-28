from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from eqar_backend.schema_generator import HttpsSchemaGenerator
from webapi.views.agency_views import AgencyList, AgencyDetail, AgencyListByFocusCountry, AgencyListByOriginCountry, \
    AgencyDecisionList
from webapi.views.country_views import CountryList, CountryDetail, CountryListByAgency, CountryListByReports
from webapi.views.institution_v2_views import *
from webapi.views.institution_views import InstitutionDetail
from webapi.views.report_v2_search_views import ReportList
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
    generator_class=HttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'webapi'

urlpatterns = [
    # Agency endpoints
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),
    url(r'^browse/agencies/focusing-to/(?P<country>[0-9]+)/$', AgencyListByFocusCountry.as_view(),
        name='agency-list-by-focuscountry'),
    url(r'^browse/agencies/based-in/(?P<country>[0-9]+)/$', AgencyListByOriginCountry.as_view(),
        name='agency-list-by-country'),
    url(r'^browse/agencies/decisions/$', AgencyDecisionList.as_view(), name='agency-decision-list'),

    # Country endpoints
    url(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    url(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),
    url(r'^browse/countries/by-agency-focus/(?P<agency>[0-9]+)/$', CountryListByAgency.as_view(),
        name='country-list-by-agency'),
    url(r'^browse/countries/by-reports/$', CountryListByReports.as_view(), name='country-list-by-reports'),

    # Institution endpoints
    url(r'^browse/institutions/$', InstitutionList.as_view(), name='institution-list'),
    url(r'^browse/institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-detail'),
    url(r'^browse/institutions/by-eter/(?P<eter_id>[^/]+)/$', InstitutionDetailByETER.as_view(),
        name='institution-eter_id-detail'),
    url(r'^browse/institutions/by-identifier/(?P<resource>[^/]+)/(?P<identifier>[^/]+)$', InstitutionDetailByIdentifier.as_view(),
        name='institution-by-identifier-detail'),
    url(r'^browse/institutions/resources/$', InstitutionIdentifierResourcesList.as_view(),
        name='institution-resources'),

    # Reports endpoints
    url(r'^browse/reports/$', ReportList.as_view(), name='report-list'),
    url(r'^browse/reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-detail'),
    url(r'^browse/reports/programme/by-institution/(?P<institution>[0-9]+)/$',
        ReportListByInstitution.as_view(), {'report_type': 'programme'},
        name='programme-report-list-by-institution'),
    url(r'^browse/reports/institutional/by-institution/(?P<institution>[0-9]+)/$',
        ReportListByInstitution.as_view(), {'report_type': 'institutional'},
        name='institutional-report-list-by-institution'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

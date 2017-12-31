from django.conf.urls import url
from webapi.views.agency_views import *
from webapi.views.country_views import *
from webapi.views.institution_views import *
from webapi.views.report_views import *

urlpatterns = [
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),
    url(r'^browse/agencies/operating-in/(?P<country>[0-9]+)/$', AgencyListByFocusCountry.as_view(),
        name='agency-list-by-focuscountry'),
    url(r'^browse/agencies/based-in/(?P<country>[0-9]+)/$', AgencyListByOriginCountry.as_view(),
        name='agency-list-by-country'),

    url(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    url(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),
    url(r'^browse/countries/by-agency/(?P<agency>[0-9]+)/$', CountryListByAgency.as_view(),
        name='country-list-by-agency'),

    url(r'^browse/institutions/$', InstitutionList.as_view(), name='institution-list'),
    url(r'^browse/institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-detail'),
    url(r'^browse/institutions/by-country/(?P<country>[0-9]+)/$', InstitutionListByCountry.as_view(),
        name='institution-list-by-country'),

    url(r'^browse/reports/by-agency/(?P<agency>[0-9]+)/$', ReportListByAgency.as_view(), name='report-list-by-agency'),
    url(r'^browse/reports/by-institution/(?P<institution>[0-9]+)/$', ReportListByInstitution.as_view(),
        name='report-list-by-institution'),
    url(r'^browse/reports/by-country/(?P<country>[0-9]+)/$', ReportListByCountry.as_view(),
        name='report-list-by-country'),
    url(r'^browse/reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-detail'),
]

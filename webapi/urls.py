from django.conf.urls import url, include
from webapi.views import *


urlpatterns = [
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),
    url(r'^browse/agencies/operating-in/(?P<country>[0-9]+)/$', AgencyListByFocusCountry.as_view(),
        name='agency-list-by-focuscountry'),
    url(r'^browse/agencies/based-in/(?P<country>[0-9]+)/$', AgencyListByOriginCountry.as_view(),
        name='agency-list-by-country'),

    url(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    url(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),
    url(r'^browse/countries/agencies-in/(?P<agency>[0-9]+)/$', CountryListByAgency.as_view(),
        name='country-list-by-agency')
]

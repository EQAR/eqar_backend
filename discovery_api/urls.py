from django.conf.urls import url

from discovery_api.views import *

urlpatterns = [
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail'),

    url(r'^browse/countries/$', CountryList.as_view(), name='country-list'),
    url(r'^browse/countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-detail'),

]
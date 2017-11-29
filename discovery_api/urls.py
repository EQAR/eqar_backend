from django.conf.urls import url

from discovery_api.views import AgencyList, AgencyDetail

urlpatterns = [
    url(r'^browse/agencies/$', AgencyList.as_view(), name='agency-list'),
    url(r'^browse/agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-detail')
]
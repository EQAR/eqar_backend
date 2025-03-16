from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from connectapi.letstrust.views import DEQARVCIssue, EBSIVCIssue
from connectapi.views import InstitutionDEQARConnectList, \
    ProviderDEQARConnectList, \
    InstitutionDetail, \
    InstitutionDetailByETER, \
    InstitutionDetailByIdentifier, \
    InstitutionIdentifierResourcesList, \
    AgencyActivityDEQARConnectList, \
    AccreditationXMLViewV2
from eqar_backend.schema_generator import HttpsSchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
       title="DEQAR - Connect API",
       default_version='v1',
       description="API documentation of the API serving the DEQAR Connect project.",
       contact=openapi.Contact(email="info@eqar.eu"),
       license=openapi.License(name="BSD License"),
    ),
    validators=['flex'],
    public=True,
    generator_class=HttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'connectapi'

urlpatterns = [
    # DEQAR Connect endpoints
    re_path(r'^providers/$', ProviderDEQARConnectList.as_view(), name='institution-deqar-connect-list'),
    re_path(r'^institutions/$', InstitutionDEQARConnectList.as_view(), name='institution-deqar-connect-list'),
    re_path(r'^institutions/(?P<pk>[0-9]+)$', InstitutionDetail.as_view(), name='institution-deqar-connect-detail'),
    re_path(r'^institutions/by-eter/(?P<eter_id>[^/]+)$', InstitutionDetailByETER.as_view(),
        name='institution-deqar-connect-eter_id-detail'),
    re_path(r'^institutions/by-identifier/(?P<resource>[^/]+)/(?P<identifier>[^/]+)$', InstitutionDetailByIdentifier.as_view(),
        name='institution-deqar-connect-by-identifier-detail'),
    re_path(r'^institutions/resources/$', InstitutionIdentifierResourcesList.as_view(),
        name='institution-deqar-connect-resources'),
    re_path(r'^activities/$', AgencyActivityDEQARConnectList.as_view(), name='agency-activity-deqar-connect-list'),

    # Europass endpoints
    re_path(r'^europass/accreditations-v2/(?P<country_code>[a-zA-Z\-]+)/$', AccreditationXMLViewV2.as_view(),
        name='europass-accreditations-v2'),

    # Let's Trust endpoints
    re_path(r'^letstrust/vc/issue/(?P<report_id>[0-9]+)$', DEQARVCIssue.as_view(), name='letstrust-vc-issue'),
    re_path(r'^letstrust/ebsi-vc/issue/(?P<report_id>[0-9]+)$', EBSIVCIssue.as_view(), name='letstrust-ebsi-vc-issue'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

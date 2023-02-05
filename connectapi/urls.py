from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from connectapi.letstrust.views import DEQARVCIssue, EBSIVCIssue
from connectapi.views import InstitutionDEQARConnectList, AgencyActivityDEQARConnectList, AccreditationXMLView, AccreditationXMLViewV2
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


class AccrediationXMLViewV2:
    pass


urlpatterns = [
    # DEQAR Connect endpoints
    url(r'^institutions/$', InstitutionDEQARConnectList.as_view(), name='institution-deqar-connect-list'),
    url(r'^activities/$', AgencyActivityDEQARConnectList.as_view(), name='agency-activity-deqar-connect-list'),

    # Europass endpoints
    url(r'^europass/accreditations/(?P<country_code>[a-zA-Z]{3})/$', AccreditationXMLView.as_view(), name='europass-accreditations'),
    url(r'^europass/accreditations-v2/(?P<country_code>[a-zA-Z]{3})/$', AccreditationXMLViewV2.as_view(),
        name='europass-accreditations-v2'),

    # Verifiable Credentials endpoints (via SSIkit)
    url(r'^letstrust/vc/issue/(?P<report_id>[0-9]+)(?:.(?P<format>json|jwt|api))?$', DEQARVCIssue.as_view(), name='letstrust-vc-issue'),
    url(r'^letstrust/ebsi-vc/issue/(?P<report_id>[0-9]+)(?:.(?P<format>json|jwt|api))?$', EBSIVCIssue.as_view(), name='letstrust-ebsi-vc-issue'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

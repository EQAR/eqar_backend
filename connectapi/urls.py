from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from connectapi.views import InstitutionDEQARConnectList, AgencyActivityDEQARConnectList

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
   permission_classes=(permissions.AllowAny,),
)

app_name = 'connectapi'

urlpatterns = [
    # DEQAR Connect endpoints
    url(r'^institutions/$', InstitutionDEQARConnectList.as_view(), name='institution-deqar-connect-list'),
    url(r'^activities/$', AgencyActivityDEQARConnectList.as_view(), name='agency-activity-deqar-connect-list'),

    # url(r'^europeana/accreditations/(?P<country_code>[a-zA-Z]{3})$', AccreditationXMLView.as_view(), name='europeana-accreditations'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

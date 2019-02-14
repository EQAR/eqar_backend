from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from adminapi.views.institution_v2_views import InstitutionAllList

app_name = 'adminapi'

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Admin API",
      default_version='v2',
      description="API documentation of the API serving the DEQAR administrative UI",
      contact=openapi.Contact(email="info@eqar.eu"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^select/institutions/$', InstitutionAllList.as_view(), name='institution-select-all'),

    # Swagger endpoints
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

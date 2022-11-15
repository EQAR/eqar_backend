from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from eqar_backend.schema_generator import HttpsSchemaGenerator
from reports.views.v1.report_detail_view import ReportDetailView
from reports.views.v1.report_search_view import ReportSearchView

schema_view = get_schema_view(
    openapi.Info(
        title="DEQAR - Reports API",
        default_version='v1',
        description="API documentation of the API serving the DEQAR website",
        contact=openapi.Contact(email="info@eqar.eu"),
        license=openapi.License(name="BSD License"),
    ),
    validators=['flex'],
    public=True,
    generator_class=HttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'reports'

urlpatterns = [
    url(r'$', ReportSearchView.as_view(), name='report-search'),
    url(r'^(?P<pk>[0-9]+)/$', ReportDetailView.as_view(), name='report-detail'),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]
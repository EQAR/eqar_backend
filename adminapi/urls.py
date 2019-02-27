from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from adminapi.views.dashboard_views import ReportsByAgency, DashboardBadgesView
from adminapi.views.institution_search_views import InstitutionAllList
from adminapi.views.institution_views import InstitutionDetail, InstitutionCreate
from adminapi.views.report_search_views import ReportList, MyReportList
from adminapi.views.report_views import ReportDetail
from adminapi.views.select_views import CountrySelectList, AgencySelectList, AgencyESGActivitySelectList, \
    LanguageSelectList, AssociationSelectList, EQARDecisionTypeSelectList, IdentifierResourceSelectList, \
    PermissionTypeSelectList, QFEHEALevelSelectList, AgencyESGActivitySelectAllList, ReportDecisionSelectList, \
    ReportStatusSelectList, InstitutionCountrySelectList, AgencySelectAllList, AgencyActivityTypeSelectList, \
    FlagSelectList

app_name = 'adminapi'

schema_view = get_schema_view(
   openapi.Info(
      title="DEQAR - Admin API",
      default_version='v1',
      description="API documentation of the API serving the DEQAR administrative UI",
      contact=openapi.Contact(email="info@eqar.eu"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Dashboard
    url(r'^reports_by_agency/$', ReportsByAgency.as_view(), name='submit-report'),
    url(r'^dashboard/badges/$', DashboardBadgesView.as_view(), name='dashboard-badges'),

    # Select Endpoints
    url(r'^select/agency/$', AgencySelectList.as_view(), name='agency-select'),
    url(r'^select/agency_all/$', AgencySelectAllList.as_view(), name='agency-select-all'),
    url(r'^select/agency_esg_activity/$', AgencyESGActivitySelectAllList.as_view(),
        name='agency-activity-select'),
    url(r'^select/agency_esg_activity/(?P<pk>[0-9]+)/$', AgencyESGActivitySelectList.as_view(),
        name='agency-activity-select'),
    url(r'^select/activity_type/$', AgencyActivityTypeSelectList.as_view(),
        name='agency-activity-type-select'),
    url(r'^select/country/$', CountrySelectList.as_view(), name='country-select'),
    url(r'^select/language/$', LanguageSelectList.as_view(), name='language-select'),
    url(r'^select/association/$', AssociationSelectList.as_view(), name='association-select'),
    url(r'^select/eqar_decision_type/$', EQARDecisionTypeSelectList.as_view(), name='decision-select'),
    url(r'^select/identifier_resource/$', IdentifierResourceSelectList.as_view(),
        name='identifier-resource-select'),
    url(r'^select/permission_type/$', PermissionTypeSelectList.as_view(), name='permission-type-select'),
    url(r'^select/qf_ehea_level/$', QFEHEALevelSelectList.as_view(), name='qf_ehea_level-select'),

    url(r'^select/institutions/$', InstitutionAllList.as_view(), name='institution-select-all'),
    url(r'^select/institutions/country/$', InstitutionCountrySelectList.as_view(), name='institution-country-select'),

    url(r'^select/report_decision/$', ReportDecisionSelectList.as_view(), name='report_decision-select'),
    url(r'^select/report_status/$', ReportStatusSelectList.as_view(), name='report_status-select'),
    url(r'^select/flag/$', FlagSelectList.as_view(), name='flag-select'),

    # Management endpoints
    url(r'^institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-edit'),
    url(r'^institutions/$', InstitutionCreate.as_view(), name='institution-create'),

    url(r'^reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-view-edit'),

    # Browse endpoints
    url(r'^browse/reports/$', ReportList.as_view(), name='report-list'),
    url(r'^browse/my-reports/$', MyReportList.as_view(), name='my-report-list'),

    # Swagger endpoints
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

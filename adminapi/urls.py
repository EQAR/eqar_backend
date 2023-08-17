from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from adminapi.views.agency_search_views import AgencyList
from adminapi.views.agency_views import AgencyESGActivityList, AgencyDetail, MyAgencyDetail, \
    AgencyDecisionFileUploadView
from adminapi.views.country_views import CountryList, CountryDetail
from adminapi.views.dashboard_views import ReportsByAgency, DashboardBadgesView
from adminapi.views.flag_views import ReportFlagList
from adminapi.views.institution_search_views import InstitutionAllList
from adminapi.views.institution_views import InstitutionDetail, InstitutionCreate
from adminapi.views.report_search_views import ReportList
from adminapi.views.report_views import ReportDetail, ReportFlagRemove, ReportCreate
from adminapi.views.select_views import CountrySelectList, AgencySelectList, AgencyESGActivitySelectList, \
    LanguageSelectList, AssociationSelectList, EQARDecisionTypeSelectList, IdentifierResourceSelectList, \
    PermissionTypeSelectList, QFEHEALevelSelectList, ReportDecisionSelectList, \
    ReportStatusSelectList, InstitutionCountrySelectList, AgencySelectAllList, AgencyActivityTypeSelectList, \
    FlagSelectList, InstitutionHistoricalRelationshipTypeSelect, QARequirementTypeSelectList, \
    InstitutionHierarchicalRelationshipTypeSelect, InstitutionOrganizationTypeSelectList, AssessmentSelectList
from eqar_backend.schema_generator import HttpsSchemaGenerator

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
    generator_class=HttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Dashboard
    url(r'^reports_by_agency/$', ReportsByAgency.as_view(), name='submit-report'),
    url(r'^dashboard/badges/$', DashboardBadgesView.as_view(), name='dashboard-badges'),

    # Select Endpoints
    url(r'^select/agency/$', AgencySelectList.as_view(), name='agency-select'),
    url(r'^select/agency_all/$', AgencySelectAllList.as_view(), name='agency-select-all'),
    url(r'^select/agency_esg_activity/$', AgencyESGActivityList.as_view(),
        name='agency-activity-select'),
    url(r'^select/agency_esg_activity/(?P<pk>[0-9]+)/$', AgencyESGActivitySelectList.as_view(),
        name='agency-activity-select'),
    url(r'^select/activity_type/$', AgencyActivityTypeSelectList.as_view(),
        name='agency-activity-type-select'),
    url(r'^select/country/$', CountrySelectList.as_view(), name='country-select'),
    url(r'^select/language/$', LanguageSelectList.as_view(), name='language-select'),
    url(r'^select/association/$', AssociationSelectList.as_view(), name='association-select'),
    url(r'^select/assessment/$', AssessmentSelectList.as_view(), name='assessment-select'),
    url(r'^select/eqar_decision_type/$', EQARDecisionTypeSelectList.as_view(), name='decision-select'),
    url(r'^select/identifier_resource/$', IdentifierResourceSelectList.as_view(),
        name='identifier-resource-select'),
    url(r'^select/permission_type/$', PermissionTypeSelectList.as_view(), name='permission-type-select'),
    url(r'^select/qf_ehea_level/$', QFEHEALevelSelectList.as_view(), name='qf_ehea_level-select'),

    url(r'^select/institutions/$', InstitutionAllList.as_view(), name='institution-select-all'),
    url(r'^select/institutions/country/$', InstitutionCountrySelectList.as_view(), name='institution-country-select'),
    url(r'^select/institutions/organization_type/$', InstitutionOrganizationTypeSelectList.as_view(),
        name='institution-org-type-select'),

    url(r'^select/report_decision/$', ReportDecisionSelectList.as_view(), name='report_decision-select'),
    url(r'^select/report_status/$', ReportStatusSelectList.as_view(), name='report_status-select'),
    url(r'^select/flag/$', FlagSelectList.as_view(), name='flag-select'),
    url(r'^select/qa_requirement_type/$', QARequirementTypeSelectList.as_view(), name='qa_requirement_type-select'),
    url(r'^select/institution_hierarchical_relationship_types/$', InstitutionHierarchicalRelationshipTypeSelect.as_view(),
        name='institution-hierarchical-relationship-type-select'),
    url(r'^select/institution_historical_relationship_types/$', InstitutionHistoricalRelationshipTypeSelect.as_view(),
        name='institution-historical-relationship-type-select'),

    # Management endpoints
    url(r'^agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-view-edit'),
    url(r'^my_agency/(?P<pk>[0-9]+)/$', MyAgencyDetail.as_view(), name='my_agency-view-edit'),

    url(r'^submit/(?P<file_type>["decision"|"decision_extra"]+)/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$',
        AgencyDecisionFileUploadView.as_view(), name='upload-agency_decision_file'),
    url(r'^institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-edit'),
    url(r'^institutions/$', InstitutionCreate.as_view(), name='institution-create'),

    url(r'^reports/$', ReportCreate.as_view(), name='report-create'),
    url(r'^reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-view-edit'),
    url(r'^reports/remove_flag/(?P<pk>[0-9]+)/$', ReportFlagRemove.as_view(), name='report-flag-delete'),

    url(r'^flags/reports/$', ReportFlagList.as_view(), name='report-flags'),

    url(r'^countries/$', CountryList.as_view(), name='country-list-create'),
    url(r'^countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-edit'),

    # Browse endpoints
    url(r'^browse/(?P<request_type>["all"|"my"]+)/reports/$', ReportList.as_view(), name='report-list'),
    url(r'^browse/(?P<request_type>["all"|"my"]+)/agencies/$', AgencyList.as_view(), name='agency-all'),

    # Swagger endpoints
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

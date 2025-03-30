from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from adminapi.views.agency_search_views import AgencyList
from adminapi.views.agency_views import AgencyESGActivityList, AgencyDetail, MyAgencyDetail, \
    AgencyDecisionFileUploadView, AgencyActivityGroupUpdateView, AgencyActivityGroupCreateView
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
    InstitutionHierarchicalRelationshipTypeSelect, InstitutionOrganizationTypeSelectList, AssessmentSelectList, \
    DegreeOutcomeSelectList, AgencyActivityGroupSelectList
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
    re_path(r'^reports_by_agency/$', ReportsByAgency.as_view(), name='submit-report'),
    re_path(r'^dashboard/badges/$', DashboardBadgesView.as_view(), name='dashboard-badges'),

    # Select Endpoints
    re_path(r'^select/agency/$', AgencySelectList.as_view(), name='agency-select'),
    re_path(r'^select/agency_all/$', AgencySelectAllList.as_view(), name='agency-select-all'),
    re_path(r'^select/agency_esg_activity/$', AgencyESGActivityList.as_view(),
        name='agency-activity-select'),
    re_path(r'^select/agency_esg_activity_by_agency/$', AgencyESGActivitySelectList.as_view(),
        name='agency-activity-select-by-agency'),
    re_path(r'^select/activity_group/$', AgencyActivityGroupSelectList.as_view(),
            name='agency-activity-group-select'),
    re_path(r'^select/activity_group_all$', AgencyActivityGroupSelectList.as_view(),
            name='agency-activity-group-select'),
    re_path(r'^select/activity_type/$', AgencyActivityTypeSelectList.as_view(),
        name='agency-activity-type-select'),
    re_path(r'^select/country/$', CountrySelectList.as_view(), name='country-select'),
    re_path(r'^select/language/$', LanguageSelectList.as_view(), name='language-select'),
    re_path(r'^select/association/$', AssociationSelectList.as_view(), name='association-select'),
    re_path(r'^select/assessment/$', AssessmentSelectList.as_view(), name='assessment-select'),
    re_path(r'^select/degree_outcome/$', DegreeOutcomeSelectList.as_view(), name='degree-outcome-select'),
    re_path(r'^select/eqar_decision_type/$', EQARDecisionTypeSelectList.as_view(), name='decision-select'),
    re_path(r'^select/identifier_resource/$', IdentifierResourceSelectList.as_view(),
        name='identifier-resource-select'),
    re_path(r'^select/permission_type/$', PermissionTypeSelectList.as_view(), name='permission-type-select'),
    re_path(r'^select/qf_ehea_level/$', QFEHEALevelSelectList.as_view(), name='qf_ehea_level-select'),

    re_path(r'^select/institutions/$', InstitutionAllList.as_view(), name='institution-select-all'),
    re_path(r'^select/institutions/country/$', InstitutionCountrySelectList.as_view(), name='institution-country-select'),
    re_path(r'^select/institutions/organization_type/$', InstitutionOrganizationTypeSelectList.as_view(),
        name='institution-org-type-select'),

    re_path(r'^select/report_decision/$', ReportDecisionSelectList.as_view(), name='report_decision-select'),
    re_path(r'^select/report_status/$', ReportStatusSelectList.as_view(), name='report_status-select'),
    re_path(r'^select/flag/$', FlagSelectList.as_view(), name='flag-select'),
    re_path(r'^select/qa_requirement_type/$', QARequirementTypeSelectList.as_view(), name='qa_requirement_type-select'),
    re_path(r'^select/institution_hierarchical_relationship_types/$', InstitutionHierarchicalRelationshipTypeSelect.as_view(),
        name='institution-hierarchical-relationship-type-select'),
    re_path(r'^select/institution_historical_relationship_types/$', InstitutionHistoricalRelationshipTypeSelect.as_view(),
        name='institution-historical-relationship-type-select'),

    # Management endpoints
    re_path(r'^agencies/(?P<pk>[0-9]+)/$', AgencyDetail.as_view(), name='agency-view-edit'),
    re_path(r'^my_agency/(?P<pk>[0-9]+)/$', MyAgencyDetail.as_view(), name='my_agency-view-edit'),

    # Group endpoints
    re_path(r'^agencies/activity_group/$', AgencyActivityGroupCreateView.as_view(), name='agency-activity-group-create'),
    re_path(r'^agencies/activity_group/(?P<pk>[0-9]+)/$', AgencyActivityGroupUpdateView.as_view(), name='agency-activity-group-edit'),

    re_path(r'^submit/(?P<file_type>["decision"|"decision_extra"]+)/(?P<pk>[0-9]+)/(?P<filename>[^/]+)$',
        AgencyDecisionFileUploadView.as_view(), name='upload-agency_decision_file'),
    re_path(r'^institutions/(?P<pk>[0-9]+)/$', InstitutionDetail.as_view(), name='institution-edit'),
    re_path(r'^institutions/$', InstitutionCreate.as_view(), name='institution-create'),

    re_path(r'^reports/$', ReportCreate.as_view(), name='report-create'),
    re_path(r'^reports/(?P<pk>[0-9]+)/$', ReportDetail.as_view(), name='report-view-edit'),
    re_path(r'^reports/remove_flag/(?P<pk>[0-9]+)/$', ReportFlagRemove.as_view(), name='report-flag-delete'),

    re_path(r'^flags/reports/$', ReportFlagList.as_view(), name='report-flags'),

    re_path(r'^countries/$', CountryList.as_view(), name='country-list-create'),
    re_path(r'^countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name='country-edit'),

    # Browse endpoints
    re_path(r'^browse/(?P<request_type>["all"|"my"]+)/reports/$', ReportList.as_view(), name='report-list'),
    re_path(r'^browse/(?P<request_type>["all"|"my"]+)/agencies/$', AgencyList.as_view(), name='agency-all'),

    # Swagger endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

]

from django.conf.urls import url

from adminapi.serializers.select_serializer import IdentifierResourceSelectSerializer
from adminapi.views.dashboard_views import ReportsByAgency
from adminapi.views.select_views import CountrySelectList, AgencySelectList, AgencyESGActivitySelectList, \
    LanguageSelectList, AssociationSelectList, EQARDecisionTypeSelectList, IdentifierResourceSelectList, \
    PermissionTypeSelectList, QFEHEALevelSelectList
from submissionapi.views import Submission, ReportFileUploadView

urlpatterns = [
    url(r'^reports_by_agency$', ReportsByAgency.as_view(), name='submit-report'),

    # Select Endpoints
    url(r'^select/agency/$', AgencySelectList.as_view(), name='agency-select'),
    url(r'^select/agency_esg_activity/(?P<pk>[0-9]+)/$', AgencyESGActivitySelectList.as_view(),
        name='agency-activity-select'),
    url(r'^select/country/$', CountrySelectList.as_view(), name='country-select'),
    url(r'^select/language', LanguageSelectList.as_view(), name='language-select'),
    url(r'^select/association', AssociationSelectList.as_view(), name='association-select'),
    url(r'^select/eqar_decision_type', EQARDecisionTypeSelectList.as_view(), name='decision-select'),
    url(r'^select/identifier_resource', IdentifierResourceSelectList.as_view(),
        name='identifier-resource-select'),
    url(r'^select/permission_type', PermissionTypeSelectList.as_view(), name='permission-type-select'),
    url(r'^select/qf_ehea_level', QFEHEALevelSelectList.as_view(), name='qf_ehea_level-select')
]

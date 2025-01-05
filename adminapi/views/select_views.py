import datetime

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.serializers.select_serializers import CountrySelectSerializer, \
    LanguageSelectSerializer, AssociationSelectSerializer, \
    EQARDecisionTypeSelectSerializer, \
    IdentifierResourceSelectSerializer, PermissionTypeSelectSerializer, QFEHEALevelSelectSerializer, \
    ReportDecisionSerializer, ReportStatusSerializer, FlagSerializer, AgencySelectSerializer, \
    AgencyESGActivitySerializer, AgencyActivityTypeSerializer, InstitutionHistoricalRelationshipTypeSerializer, \
    CountryQARequirementTypeSerializer, InstitutionHierarchicalRelationshipTypeSerializer, \
    InstitutionOrganizationTypeSerializer, AssessmentSerializer, DegreeOutcomeSelectSerializer
from agencies.models import Agency, AgencyProxy, AgencyESGActivity, AgencyActivityType
from countries.models import Country, CountryQARequirementType
from institutions.models import InstitutionHistoricalRelationshipType, InstitutionHierarchicalRelationshipType, \
    InstitutionOrganizationType
from lists.models import Language, Association, EQARDecisionType, IdentifierResource, PermissionType, QFEHEALevel, Flag, \
    Assessment, DegreeOutcome
from reports.models import ReportDecision, ReportStatus


class AgencySelectList(generics.ListAPIView):
    serializer_class = AgencySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_primary', 'acronym_primary')

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Agency.objects.all().order_by('acronym_primary')
        else:
            submitting_agency = user.deqarprofile.submitting_agency
            agency_proxies = AgencyProxy.objects.filter(
                Q(submitting_agency=submitting_agency) &
                (Q(proxy_to__gte=datetime.date.today()) | Q(proxy_to__isnull=True)))
            return Agency.objects.filter(allowed_agency__in=agency_proxies).order_by('acronym_primary')


class AgencySelectAllList(generics.ListAPIView):
    serializer_class = AgencySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_primary', 'acronym_primary')
    queryset = Agency.objects.all()


class AgencyESGActivitySelectList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('activity',)

    def get_queryset(self, *args, **kwargs):
        agencies = self.request.query_params.getlist('agencies', [])
        return AgencyESGActivity.objects.filter(agency__id__in=agencies).order_by('agency', 'activity')


class AgencyActivityTypeSelectList(generics.ListAPIView):
    serializer_class = AgencyActivityTypeSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)
    queryset = AgencyActivityType.objects.all().order_by('type')


class CountrySelectList(generics.ListAPIView):
    serializer_class = CountrySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_english',)
    queryset = Country.objects.all().order_by('name_english')


class InstitutionCountrySelectList(generics.ListAPIView):
    serializer_class = CountrySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_english',)
    queryset = Country.objects.all().order_by('name_english')

    def get_queryset(self):
        return Country.objects.filter(institutioncountry__isnull=False).distinct()


class InstitutionOrganizationTypeSelectList(generics.ListAPIView):
    serializer_class = InstitutionOrganizationTypeSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)
    queryset = InstitutionOrganizationType.objects.all().order_by('id')


class LanguageSelectList(generics.ListAPIView):
    serializer_class = LanguageSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('language_name_en',)
    queryset = Language.objects.all().order_by('language_name_en')


class AssociationSelectList(generics.ListAPIView):
    serializer_class = AssociationSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('association',)
    queryset = Association.objects.all().order_by('id')


class ReportDecisionSelectList(generics.ListAPIView):
    serializer_class = ReportDecisionSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('decision',)
    queryset = ReportDecision.objects.all().order_by('id')


class EQARDecisionTypeSelectList(generics.ListAPIView):
    serializer_class = EQARDecisionTypeSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)
    queryset = EQARDecisionType.objects.all().order_by('id')


class ReportStatusSelectList(generics.ListAPIView):
    serializer_class = ReportStatusSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('status',)
    queryset = ReportStatus.objects.all().order_by('id')


class IdentifierResourceSelectList(generics.ListAPIView):
    serializer_class = IdentifierResourceSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('resource',)
    queryset = IdentifierResource.objects.all().order_by('resource')


class PermissionTypeSelectList(generics.ListAPIView):
    serializer_class = PermissionTypeSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)
    queryset = PermissionType.objects.all().order_by('type')


class QFEHEALevelSelectList(generics.ListAPIView):
    serializer_class = QFEHEALevelSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('level',)
    queryset = QFEHEALevel.objects.all().order_by('code')


class FlagSelectList(generics.ListAPIView):
    serializer_class = FlagSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('flag',)
    queryset = Flag.objects.all()


class QARequirementTypeSelectList(generics.ListAPIView):
    serializer_class = CountryQARequirementTypeSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('qa_requirement_type',)
    queryset = CountryQARequirementType.objects.all()


class AssessmentSelectList(generics.ListAPIView):
    serializer_class = AssessmentSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('assessment',)
    queryset = Assessment.objects.all().order_by('id')


class DegreeOutcomeSelectList(generics.ListAPIView):
    serializer_class = DegreeOutcomeSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('outcome',)
    queryset = DegreeOutcome.objects.all().order_by('id')


class InstitutionHierarchicalRelationshipTypeSelect(generics.ListAPIView):
    serializer_class = InstitutionHierarchicalRelationshipTypeSerializer
    queryset = InstitutionHierarchicalRelationshipType.objects.all()
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)


class InstitutionHistoricalRelationshipTypeSelect(APIView):

    @swagger_auto_schema(responses={'200': InstitutionHistoricalRelationshipTypeSerializer})
    def get(self, request, format=None):
        response = []
        for idx, relationship_type in enumerate(InstitutionHistoricalRelationshipType.objects.all().order_by('id')):
            response.append({
                'id': idx*2+1,
                'relationship_type_id': relationship_type.pk,
                'relationship': relationship_type.type_from,
                'institution_direction': 'source'
            })
            response.append({
                'id': idx*2+2,
                'relationship_type_id': relationship_type.pk,
                'relationship': relationship_type.type_to,
                'institution_direction': 'target'
            })
        return Response(data=response, status=200)

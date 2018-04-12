import datetime

from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404

from adminapi.serializers.select_serializer import CountrySelectSerializer, AgencySelectSerializer, \
    AgencyESGActivitySerializer, LanguageSelectSerializer, AssociationSelectSerializer, EQARDecisionTypeSelectSerializer, \
    IdentifierResourceSelectSerializer, PermissionTypeSelectSerializer, QFEHEALevelSelectSerializer, \
    ReportDecisionSerializer, ReportStatusSerializer
from agencies.models import Agency, AgencyProxy, AgencyESGActivity
from countries.models import Country
from lists.models import Language, Association, EQARDecisionType, IdentifierResource, PermissionType, QFEHEALevel
from reports.models import ReportDecision, ReportStatus


class AgencySelectList(generics.ListAPIView):
    serializer_class = AgencySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_primary', 'acronym_primary')

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        agency_proxies = AgencyProxy.objects.filter(
            Q(submitting_agency=submitting_agency) &
            (Q(proxy_to__gte=datetime.date.today()) | Q(proxy_to__isnull=True)))
        return Agency.objects.filter(allowed_agency__in=agency_proxies).order_by('acronym_primary')


class AgencyESGActivitySelectAllList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('activity',)

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        agency_proxies = AgencyProxy.objects.filter(
            Q(submitting_agency=submitting_agency) &
            (Q(proxy_to__gte=datetime.date.today()) | Q(proxy_to__isnull=True)))
        agencies = Agency.objects.filter(allowed_agency__in=agency_proxies).order_by('acronym_primary')
        return AgencyESGActivity.objects.filter(agency__in=agencies).order_by('agency', 'activity')


class AgencyESGActivitySelectList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('activity',)

    def get_queryset(self):
        agency = get_object_or_404(Agency, pk=self.kwargs['pk'])
        return AgencyESGActivity.objects.filter(agency=agency).order_by('activity')


class CountrySelectList(generics.ListAPIView):
    serializer_class = CountrySelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('name_english',)
    queryset = Country.objects.all().order_by('name_english')


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
    queryset = Association.objects.all().order_by('association')


class ReportDecisionSelectList(generics.ListAPIView):
    serializer_class = ReportDecisionSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('decision',)
    queryset = ReportDecision.objects.all().order_by('decision')


class EQARDecisionTypeSelectList(generics.ListAPIView):
    serializer_class = EQARDecisionTypeSelectSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('type',)
    queryset = EQARDecisionType.objects.all().order_by('type')


class ReportStatusSelectList(generics.ListAPIView):
    serializer_class = ReportStatusSerializer
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ('status',)
    queryset = ReportStatus.objects.all().order_by('status')


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
    queryset = QFEHEALevel.objects.all().order_by('level')
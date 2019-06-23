import datetime
import re

from django.db.models import Q
from django.utils.timezone import now
from django_filters import rest_framework as filters
from drf_rw_serializers.generics import RetrieveUpdateAPIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from adminapi.serializers.agency_serializers import AgencyReadSerializer, AgencyListSerializer
from adminapi.serializers.select_serializers import AgencyESGActivitySerializer
from agencies.models import Agency, AgencyActivityType, AgencyProxy, AgencyESGActivity
from countries.models import Country


class AgencyESGActivityFilterClass(filters.FilterSet):
    agency = filters.ModelChoiceFilter(field_name='agency', queryset=Agency.objects.all())
    activity = filters.CharFilter(label='Activity', method='search_activity')
    activity_type = filters.ModelChoiceFilter(field_name='activity_type', queryset=AgencyActivityType.objects.all())

    def search_activity(self, queryset, name, value):
        return queryset.filter(activity__icontains=value)

    class Meta:
        model = AgencyESGActivity
        fields = ['agency', 'activity', 'activity_type']


class AgencyESGActivityList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering = ('agency', 'activity')
    filter_class = AgencyESGActivityFilterClass

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        agency_proxies = AgencyProxy.objects.filter(
            Q(submitting_agency=submitting_agency) &
            (Q(proxy_to__gte=datetime.date.today()) | Q(proxy_to__isnull=True)))
        agencies = Agency.objects.filter(allowed_agency__in=agency_proxies).order_by('acronym_primary')
        return AgencyESGActivity.objects.filter(agency__in=agencies).order_by('agency', 'activity')


class AgencyFilterClass(filters.FilterSet):
    active = filters.BooleanFilter(label='active', method='filter_active')
    year = filters.CharFilter(label='Year', method='filter_agency_year')
    query = filters.CharFilter(label='Query', method='search_agency')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(), method='filter_country')

    def filter_active(self, queryset, name, value):
        return queryset.filter(
            Q(registration_valid_to__isnull=True) |
            Q(registration_valid_to__gt=now())
        )

    def filter_country(self, queryset, name, value):
        return queryset.filter(
            Q(country=value)
        )

    def filter_agency_year(self, queryset, name, value):
        if re.search(r"[1-2][0-9]{3}$", value):
            return queryset.filter(
                Q(registration_start__year__lte=value) & Q(registration_valid_to__year__gte=value)
            )
        else:
            return Agency.objects.none()

    def search_agency(self, queryset, name, value):
        return queryset.filter(
            Q(agencyname__agencynameversion__name__icontains=value) |
            Q(agencyname__agencynameversion__name_transliterated__icontains=value) |
            Q(agencyname__agencynameversion__acronym__icontains=value) |
            Q(agencyname__agencynameversion__acronym_transliterated__icontains=value)
        ).distinct()

    class Meta:
        model = Agency
        fields = ['query']


class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.filter(is_registered=True)
    serializer_class = AgencyListSerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    filter_class = AgencyFilterClass
    ordering_fields = ('deqar_id', 'name_primary', 'acronym_primary', 'country__name_english', 'registration_valid_to')
    ordering = ('acronym_primary', 'name_primary')


class AgencyDetail(RetrieveUpdateAPIView):
    queryset = Agency.objects.all()
    # serializer_class = AgencyReadSerializer
    read_serializer_class = AgencyReadSerializer
    # write_serializer_class = InstitutionWriteSerializer

    @swagger_auto_schema(responses={'200': AgencyReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(AgencyDetail, self).get(request, *args, **kwargs)


class MyAgencyDetail(RetrieveUpdateAPIView):
    queryset = Agency.objects.all()
    # serializer_class = AgencyReadSerializer
    read_serializer_class = AgencyReadSerializer
    # write_serializer_class = InstitutionWriteSerializer

    def get_object(self):
        return self.request.user.deqarprofile.submitting_agency.agency

    @swagger_auto_schema(responses={'200': AgencyReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(MyAgencyDetail, self).get(request, *args, **kwargs)


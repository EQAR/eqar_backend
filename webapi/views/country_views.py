import datetime
from django.db.models import Q, Count
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from agencies.models import AgencyFocusCountry
from countries.models import Country
from lists.models import PermissionType
from webapi.serializers.agency_serializers import AgencyFocusCountrySerializer
from webapi.serializers.country_serializers import CountryDetailSerializer, CountryLargeListSerializer


class CountryFilterClass(filters.FilterSet):
    external_qaa = filters.ModelChoiceFilter(name='external_QAA_is_permitted', queryset=PermissionType.objects.all())
    european_approach = filters.ModelChoiceFilter(name='european_approach_is_permitted', queryset=PermissionType.objects.all())
    eqar_governmental_member = filters.BooleanFilter(name='eqar_governmental_member_start',
                                                     method='filter_eqar_governmental_member')

    def filter_eqar_governmental_member(self, queryset, name, value):
        return queryset.filter(eqar_governmental_member_start__isnull=not value)

    class Meta:
        model = Country
        fields = ['external_qaa', 'european_approach', 'eqar_governmental_member']


class CountryList(generics.ListAPIView):
    """
        Returns a list of countries where agencies are located.
    """
    serializer_class = CountryLargeListSerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering_fields = ('name_english', 'agency__count')
    ordering = ('name_english',)
    filter_class = CountryFilterClass

    def get_queryset(self):
        qs = Country.objects.exclude(agency=None).annotate(Count('agency'))
        return qs


class CountryListByAgency(generics.ListAPIView):
    """
        Returns a list of countries appears as focus country.
    """
    serializer_class = AgencyFocusCountrySerializer

    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            qs = AgencyFocusCountry.objects.filter(agency=self.kwargs['agency'])
            return qs
        else:
            qs = AgencyFocusCountry.objects.filter(agency=self.kwargs['agency']).filter(
                Q(country_valid_to__isnull=True) |
                Q(country_valid_to__gt=datetime.datetime.now())
            )
            return qs


class CountryDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected country.
    """
    queryset = Country.objects.all()
    serializer_class = CountryDetailSerializer

    def get_queryset(self):
        qs = Country.objects.all()
        qs = qs.select_related('external_QAA_is_permitted', 'european_approach_is_permitted')
        qs = qs.prefetch_related('countryqarequirement_set', 'countryqaaregulation_set', 'countryhistoricaldata_set')
        return qs
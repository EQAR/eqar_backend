
from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from agencies.models import Agency
from webapi.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer
from webapi.serializers.country_serializers import CountryListSerializer, CountryDetailSerializer
from lists.models import Country


class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name_primary', 'acronym_primary')
    ordering = ('name_primary',)


class AgencyListByFocusCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR operating in the submitted country.
    """
    def get_queryset(self):
        return Agency.objects.filter(Q(agencyfocuscountry__country=self.kwargs['country']))


class AgencyListByOriginCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR based in the submitted country.
    """
    def get_queryset(self):
        return Agency.objects.filter(Q(country=self.kwargs['country']))


class AgencyDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected agency.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyDetailSerializer


class CountryList(generics.ListAPIView):
    """
        Returns a list of countries which appear either as a location or as a focus country of agencies.
    """
    serializer_class = CountryListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('country_name_en', 'alpha2', 'alpha3')
    ordering = ('country_name_en',)

    def get_queryset(self):
        return Country.objects.filter(Q(agencyfocuscountry__isnull=False) |
                                      Q(agency__agency__country__isnull=False)).distinct()


class CountryListByAgency(CountryList):
    """
        Returns a list of countries where the given agency operates in.
    """
    def get_queryset(self):
        return Country.objects.filter(agencyfocuscountry__agency=self.kwargs['agency']).all()


class CountryDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected country.
    """
    queryset = Country.objects.all()
    serializer_class = CountryDetailSerializer


from django.db.models import Q
from rest_framework import generics

from agencies.models import Agency
from discovery_api.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer
from discovery_api.serializers.country_serializers import CountryListSerializer, CountryDetailSerializer
from lists.models import Country


class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.all().order_by()
    serializer_class = AgencyListSerializer


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

    def get_queryset(self):
        return Country.objects.filter(Q(agencyfocuscountry__isnull=False) |
                                      Q(agency__agency__country__isnull=False)).distinct().order_by('country_name_en')


class CountryDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected country.
    """
    queryset = Country.objects.all()
    serializer_class = CountryDetailSerializer

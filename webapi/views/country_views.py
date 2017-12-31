from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from countries.models import Country
from webapi.serializers.country_serializers import CountryListSerializer, CountryDetailSerializer


class CountryList(generics.ListAPIView):
    """
        Returns a list of countries which appear either as a location or as a focus country of agencies.
    """
    serializer_class = CountryListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name_english', 'alpha2', 'alpha3')
    ordering = ('name_english',)

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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework import filters

from adminapi.serializers.country_serializer import CountryListSerializer
from countries.models import Country


class CountryList(generics.ListCreateAPIView):
    serializer_class = CountryListSerializer
    filter_backends = (OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ['ehea_is_member', 'external_QAA_is_permitted', 'european_approach_is_permitted',
                        'ehea_key_commitment']
    ordering = ['name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member']
    search_fields = ['name_english', 'iso_3166_alpha2', 'iso_3166_alpha3']
    queryset = Country.objects.all()

from datetime import datetime

from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters

from adminapi.serializers.institution_serializer import InstitutionSelectListSerializer
from countries.models import Country
from institutions.models import Institution
from lists.models import QFEHEALevel


class InstitutionSelectFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Query', method='search_institution')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(), method='filter_country')
    qf_ehea_level = filters.ModelChoiceFilter(label='QF EHEA Level', queryset=QFEHEALevel.objects.all(),
                                              method='filter_qf_ehea_level')

    def search_institution(self, queryset, name, value):
        return queryset.filter(
            Q(institutionname__name_official__icontains=value) |
            Q(institutionname__name_official_transliterated__icontains=value) |
            Q(institutionname__name_english__icontains=value) |
            Q(institutionname__acronym__icontains=value)
        )

    def filter_country(self, queryset, name, value):
        return queryset.filter(
            Q(institutioncountry__country=value)
        )

    def filter_qf_ehea_level(self, queryset, name, value):
        return queryset.filter(institutionqfehealevel__qf_ehea_level=value)

    class Meta:
        model = Institution
        fields = ['query', 'country', 'qf_ehea_level']


class InstitutionSelectList(generics.ListAPIView):
    serializer_class = InstitutionSelectListSerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering_fields = ('name_primary',)
    ordering = ('name_primary',)
    queryset = Institution.objects.all().order_by('name_primary')
    filter_class = InstitutionSelectFilterClass

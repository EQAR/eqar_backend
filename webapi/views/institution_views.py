import re

import datetime

from datedelta import datedelta
from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from agencies.models import Agency, AgencyESGActivity
from countries.models import Country
from institutions.models import Institution
from lists.models import QFEHEALevel
from reports.models import ReportStatus
from webapi.serializers.institution_serializers import InstitutionListSerializer, InstitutionDetailSerializer


class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Query', method='search_institution')
    agency = filters.ModelChoiceFilter(label='Agency', queryset=Agency.objects.all(), method='filter_agency')
    esg_activity = filters.ModelChoiceFilter(label='ESGActivity', queryset=AgencyESGActivity.objects.all(),
                                             method='filter_esg_activity')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(), method='filter_country')
    qf_ehea_level = filters.ModelChoiceFilter(label='QF EHEA Level', queryset=QFEHEALevel.objects.all(),
                                              method='filter_qf_ehea_level')
    status = filters.ModelChoiceFilter(label='Report Status', queryset=ReportStatus.objects.all(),
                                       method='filter_report_status')
    report_year = filters.CharFilter(label='Report Year', method='filter_report_date')
    focus_country_is_crossborder = filters.BooleanFilter(label='Focus Country Cross-Border',
                                                         method='filter_focus_country_is_crossborder')

    def search_institution(self, queryset, name, value):
        include_history = self.request.query_params.get('history', True)

        if include_history == 'true':
            return queryset.filter(
                Q(institutionname__name_official__icontains=value) |
                Q(institutionname__name_official_transliterated__icontains=value) |
                Q(institutionname__name_english__icontains=value) |
                Q(institutionname__acronym__icontains=value) |
                Q(institutioncountry__country__name_english__icontains=value) |
                Q(institutioncountry__city__icontains=value) |
                (
                    Q(institutionhistoricaldata__field=4) &
                    Q(institutionhistoricaldata__value__icontains=value)
                ) | (
                    Q(institutionhistoricaldata__field=5) &
                    Q(institutionhistoricaldata__value__icontains=value)
                ) | (
                    Q(institutionhistoricaldata__field=6) &
                    Q(institutionhistoricaldata__value__icontains=value)
                ) | (
                    Q(institutionhistoricaldata__field=7) &
                    Q(institutionhistoricaldata__value__icontains=value)
                )
            )
        else:
            return queryset.filter(
                (
                    Q(institutionname__name_official__icontains=value) & (
                        Q(institutionname__name_valid_to__isnull=True) |
                        Q(institutionname__name_valid_to__gte=datetime.datetime.now())
                    )
                ) | (
                    Q(institutionname__name_english__icontains=value) & (
                        Q(institutionname__name_valid_to__isnull=True) |
                        Q(institutionname__name_valid_to__gte=datetime.datetime.now())
                    )
                ) | (
                    Q(institutionname__name_official_transliterated__icontains=value) & (
                        Q(institutionname__name_valid_to__isnull=True) |
                        Q(institutionname__name_valid_to__gte=datetime.datetime.now())
                    )
                ) | (
                    Q(institutionname__acronym__icontains=value) & (
                        Q(institutionname__name_valid_to__isnull=True) |
                        Q(institutionname__name_valid_to__gte=datetime.datetime.now())
                    )
                ) | (
                    Q(institutioncountry__country__name_english__icontains=value) & (
                            Q(institutioncountry__country_valid_to__isnull=True) |
                            Q(institutioncountry__country_valid_to__gte=datetime.datetime.now())
                    )
                ) | (
                    Q(institutioncountry__city__icontains=value) & (
                            Q(institutioncountry__country_valid_to__isnull=True) |
                            Q(institutioncountry__country_valid_to__gte=datetime.datetime.now())
                    )
                )
            )

    def filter_agency(self, queryset, name, value):
        return queryset.filter(reports__agency=value)

    def filter_esg_activity(self, queryset, name, value):
        return queryset.filter(reports__agency_esg_activity=value)

    def filter_country(self, queryset, name, value):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return queryset.filter(
                Q(institutioncountry__country=value) |
                Q(reports__programme__countries=value)
            )
        else:
            return queryset.filter(
                Q(institutioncountry__country=value) & (
                    Q(institutioncountry__country_valid_to__isnull=True) |
                    Q(institutioncountry__country_valid_to__gte=datetime.datetime.now())
                ) |
                Q(reports__programme__countries=value)
            )

    def filter_qf_ehea_level(self, queryset, name, value):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return queryset.filter(institutionqfehealevel__qf_ehea_level=value)
        else:
            return queryset.filter(
                Q(institutionqfehealevel__qf_ehea_level=value) & (
                    Q(institutionqfehealevel__qf_ehea_level_valid_to__isnull=True) |
                    Q(institutionqfehealevel__qf_ehea_level_valid_to__gte=datetime.datetime.now())
                )
            )

    def filter_report_status(self, queryset, name, value):
        return queryset.filter(reports__status=value)

    def filter_focus_country_is_crossborder(self, queryset, name, value):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return queryset.filter(
                Q(reports__agency__agencyfocuscountry__country_is_crossborder__isnull=value) | (
                    Q(reports__agency__agencyhistoricaldata__field=8) &
                    Q(reports__agency__agencyhistoricaldata__value='True')
                )
            )
        else:
            return queryset.filter(
                Q(reports__agency__agencyfocuscountry__country_is_crossborder__isnull=value) & (
                    Q(reports__agency__agencyfocuscountry__country_valid_to__isnull=True) |
                    Q(reports__agency__agencyfocuscountry__country_valid_to__gte=datetime.datetime.now())
                )
            )

    def filter_report_date(self, queryset, name, value):
        if re.search(r"[1-2][0-9]{3}$", value):
            return queryset.filter(reports__valid_from__year__lte=value, reports__valid_to__year__gte=value)
        else:
            return Institution.objects.none()

    class Meta:
        model = Institution
        fields = ['query', 'agency', 'esg_activity', 'country', 'qf_ehea_level', 'status', 'report_year',
                  'focus_country_is_crossborder']


class InstitutionList(generics.ListAPIView):
    """
    Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    serializer_class = InstitutionListSerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering_fields = ('name_primary',)
    ordering = ('name_primary',)
    filter_class = InstitutionFilterClass

    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return Institution.objects.filter(reports__isnull=False).distinct()
        else:
            qs = Institution.objects.filter(
                Q(reports__isnull=False) &
                (
                    Q(reports__valid_to__gte=datetime.datetime.now()) | (
                        Q(reports__valid_to__isnull=True) &
                        Q(reports__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            ).distinct()
            qs = qs.select_related('eter')
            qs = qs.prefetch_related('institutioncountry_set')
            qs = qs.prefetch_related('relationship_parent')
            qs = qs.prefetch_related('relationship_child')
            return qs


class InstitutionDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    serializer_class = InstitutionDetailSerializer

    def get_queryset(self):
        qs = Institution.objects.filter(pk=self.kwargs['pk'])
        return qs

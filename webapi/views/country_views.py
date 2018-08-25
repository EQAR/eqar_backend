import datetime
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from agencies.models import AgencyFocusCountry, Agency
from countries.models import Country
from institutions.models import Institution
from lists.models import PermissionType
from reports.models import Report
from webapi.serializers.agency_serializers import AgencyFocusCountrySerializer
from webapi.serializers.country_serializers import CountryDetailSerializer, CountryLargeListSerializer, \
    CountryReportListSerializer, CountryStatsSerializer


class CountryFilterClass(filters.FilterSet):
    external_qaa = filters.ModelChoiceFilter(field_name='external_QAA_is_permitted',
                                             queryset=PermissionType.objects.all())
    european_approach = filters.ModelChoiceFilter(field_name='european_approach_is_permitted',
                                                  queryset=PermissionType.objects.all())
    eqar_governmental_member = filters.BooleanFilter(field_name='eqar_governmental_member_start',
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
    ordering_fields = ('name_english', 'agency_count')
    ordering = ('name_english',)
    filter_class = CountryFilterClass
    pagination_class = None

    def get_queryset(self):
        qs = Country.objects.filter(ehea_is_member=True).annotate(
            agency_count=Count('agency', filter=Q(agency__is_registered=True))
        )
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


class CountryListByReports(generics.ListAPIView):
    """
        Returns a list of countries appearing in reports.
    """
    serializer_class = CountryReportListSerializer
    pagination_class = None

    def get_queryset(self):
        include_history = self.request.query_params.get('history', False)

        sql = '''
            SELECT
            id, iso_3166_alpha2, iso_3166_alpha3, name_english, COUNT(institution_id) as inst_count
            FROM
            (SELECT DISTINCT deqar_countries."id",
                deqar_countries.iso_3166_alpha2,
                deqar_countries.iso_3166_alpha3,
                deqar_countries.name_english,
                deqar_institution_countries.institution_id
            FROM deqar_countries
                INNER JOIN deqar_institution_countries ON
                  deqar_countries."id" = deqar_institution_countries.country_id
                INNER JOIN deqar_reports_institutions ON
                  deqar_institution_countries.institution_id = deqar_reports_institutions.institution_id
                INNER JOIN deqar_reports ON
                  deqar_reports_institutions.report_id = deqar_reports."id"
            WHERE deqar_reports.flag_id != 3
            %s
            GROUP BY deqar_countries."id",
                deqar_countries.iso_3166_alpha2,
                deqar_countries.iso_3166_alpha3,
                deqar_countries.name_english,
                deqar_institution_countries.institution_id
            ORDER BY name_english) AS filtered_countries
            GROUP BY id, iso_3166_alpha2, iso_3166_alpha3, name_english
            ORDER BY name_english
        '''

        if include_history:
            sql %= ""
            qs = Country.objects.raw(sql)
        else:
            history_sql = '''AND (deqar_institution_countries.country_valid_to >= %s OR
                             deqar_institution_countries.country_valid_to IS NULL)'''
            sql %= history_sql
            qs = Country.objects.raw(sql, params=[datetime.datetime.now()])
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


class CountryStatsView(APIView):
    """
        Returns the number of institutions and reports per country and per country plus agency.
    """
    @swagger_auto_schema(responses={200: CountryStatsSerializer()})
    def get(self, request, country):
        country_counter = {}
        agency_based_in_counters = []
        agency_focused_on_counters = []

        country_record = get_object_or_404(Country, pk=country)
        agencies_based_in = Agency.objects.filter(country=country)
        agencies_focused_on = Agency.objects.filter(agencyfocuscountry__country=country)

        reports_count = Report.objects.filter(
            institutions__institutioncountry__country=country_record
        ).distinct().count()
        institution_count = Institution.objects.filter(
            Q(has_report=True) & (
                Q(institutioncountry__country=country_record) |
                Q(reports__programme__countries=country_record)
            )
        ).distinct().count()
        country_counter['reports'] = reports_count
        country_counter['institutions'] = institution_count

        # KILL
        for agency in agencies_based_in:
            counter = {}
            reports_count = Report.objects.filter(agency=agency).count()
            institution_count = Institution.objects.filter(
                Q(has_report=True) & Q(reports__agency=agency)
            ).distinct().count()
            counter['agency_id'] = agency.id
            counter['reports'] = reports_count
            counter['institutions'] = institution_count
            agency_based_in_counters.append(counter)

        for agency in agencies_focused_on:
            counter = {}
            reports_count = Report.objects.filter(agency=agency).count()
            institution_count = Institution.objects.filter(
                Q(has_report=True) & Q(reports__agency=agency)
            ).distinct().count()
            counter['agency_id'] = agency.id
            counter['reports'] = reports_count
            counter['institutions'] = institution_count
            agency_focused_on_counters.append(counter)

        return Response(CountryStatsSerializer({
            'country_counter': country_counter,
            'country_agency_based_in_counter': agency_based_in_counters,
            'country_agency_focused_on_counter': agency_focused_on_counters
        }).data)

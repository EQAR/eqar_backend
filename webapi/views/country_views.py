import datetime
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from agencies.models import AgencyFocusCountry
from countries.models import Country
from lists.models import PermissionType
from webapi.inspectors.country_list_inspector import CountryListInspector
from webapi.serializers.agency_serializers import AgencyFocusCountrySerializer
from webapi.serializers.country_serializers import CountryDetailSerializer, CountryLargeListSerializer, \
    CountryReportListSerializer


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


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[CountryListInspector],
))
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
            id, iso_3166_alpha2, iso_3166_alpha3, ehea_is_member, name_english, 
            has_full_institution_list, ehea_key_commitment_id,
            COUNT(institution_id) as inst_count
            FROM
            (SELECT DISTINCT deqar_countries."id",
                deqar_countries.iso_3166_alpha2,
                deqar_countries.iso_3166_alpha3,
                deqar_countries.ehea_is_member,
                deqar_countries.name_english,
                deqar_countries.has_full_institution_list,
                deqar_countries.ehea_key_commitment_id,                
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
                deqar_countries.has_full_institution_list,
                deqar_countries.ehea_key_commitment_id, 
                deqar_institution_countries.institution_id
            ORDER BY name_english) AS filtered_countries
            GROUP BY id, iso_3166_alpha2, iso_3166_alpha3, name_english, 
                has_full_institution_list, ehea_key_commitment_id, ehea_is_member
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

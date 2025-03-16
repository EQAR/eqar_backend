import json
import datetime

from collections import defaultdict

from django.http import Http404
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.exceptions import ParseError, APIException
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from eqar_backend.meilisearch import MeiliClient
from meilisearch.errors import MeilisearchApiError

from webapi.v2.views.meili_solr_view import MeiliSolrBackportView

from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField

from agencies.models import Agency, AgencyESGActivity, AgencyActivityType
from countries.models import Country
from eqar_backend.searchers import Searcher
from institutions.models import Institution, InstitutionIdentifier
from lists.models import QFEHEALevel, IdentifierResource
from reports.models import ReportStatus

from webapi.inspectors.institution_search_inspector import InstitutionSearchInspector
from webapi.v2.serializers.institution_serializers import InstitutionResourceSerializer, InstitutionDetailSerializer



class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search')
    country = filters.ModelChoiceFilter(label='Country', queryset=Country.objects.all(),
                                        to_field_name='name_english')
    country_id = filters.ModelChoiceFilter(label='Country ID', queryset=Country.objects.all(),
                                           to_field_name='id')
    agency = filters.ModelChoiceFilter(label='Agency', queryset=Agency.objects.all(),
                                       to_field_name='acronym_primary')
    agency_id = filters.ModelChoiceFilter(label='Agency ID', queryset=Agency.objects.all(),
                                          to_field_name='id')
    activity = filters.ModelChoiceFilter(label='Activity', queryset=AgencyESGActivity.objects.all(),
                                         to_field_name='activity_display')
    activity_id = filters.ModelChoiceFilter(label='Activity ID', queryset=AgencyESGActivity.objects.all(),
                                            to_field_name='id')
    activity_type = filters.ModelChoiceFilter(label='Activity Type', queryset=AgencyActivityType.objects.all(),
                                              to_field_name='type')
    activity_type_id = filters.ModelChoiceFilter(label='Activity Type ID', queryset=AgencyActivityType.objects.all(),
                                                 to_field_name='id')
    status = filters.ModelChoiceFilter(label='Report Status', queryset=ReportStatus.objects.all(),
                                       to_field_name='status')
    status_id = filters.ModelChoiceFilter(label='Report Status ID', queryset=ReportStatus.objects.all(),
                                          to_field_name='id')
    qf_ehea_level = filters.ModelChoiceFilter(label='QF EHEA Level', queryset=QFEHEALevel.objects.all(),
                                              to_field_name='level')
    qf_ehea_level_id = filters.ModelChoiceFilter(label='QF EHEA Level ID', queryset=QFEHEALevel.objects.all(),
                                                 to_field_name='id')
    crossborder = filters.BooleanFilter(label='Crossborder')
    other_provider = filters.BooleanFilter(label='Other Provider')

    ordering = OrderingFilter(
        fields=(
            'score',
            'name_sort',
            'founding_date',
            'closure_date',
            'country'
        )
    )


@method_decorator(name='get', decorator=swagger_auto_schema(
    filter_inspectors=[InstitutionSearchInspector]
))
class InstitutionList(MeiliSolrBackportView):
    """
    Returns a list of all the institutions to which a report was submitted in DEQAR

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = InstitutionFilterClass

    MEILI_INDEX = 'INDEX_INSTITUTIONS'
    ORDERING_MAPPING = {
        'name_sort': 'name_sort',
        'founding_date': 'founding_date',
        'closure_date': 'closure_date',
        'country': 'locations.country.name_english',
    }
    FACET_NAMES = {
        'locations.country.id': 'country_facet',
        'qf_ehea_levels': 'qf_ehea_level_facet',
        'agencies.id': 'reports_agencies',
        'status': 'status_facet',
        'activity_types': 'activity_type_facet',
        'crossborder': 'crossborder_facet',
        'is_other_provider': 'other_provider_facet',
    }
    FACET_LOOKUP = {
        'agencies.id':          { 'model': Agency,            'attribute': 'acronym_primary' },
        'locations.country.id': { 'model': Country,           'attribute': 'name_english' },
    }


    def make_filters(self, request):

        # this view shows only institutions with reports
        filters = [ 'has_report = True' ]

        if country_id := self.lookup_object(Country, 'name_english', 'country', 'id', 'country_id'):
            filters.append(f'locations.country.id = {country_id}')

        if request.query_params.get('activity', None) or request.query_params.get('activity_id', None):
            raise ParseError(detail='filtering by activity name or ID is no longer supported by the Web API')

        if agency_id := self.lookup_object(Agency, 'acronym_primary', 'agency', 'id', 'agency_id'):
            filters.append(f'agencies.id = {agency_id}')

        if status := self.lookup_object(ReportStatus, 'id', 'status_id', 'status', 'status'):
            filters.append(f'status = "{status}"')

        if qf_ehea_level := self.lookup_object(QFEHEALevel, 'id', 'qf_ehea_level_id', 'level', 'qf_ehea_level'):
            filters.append(f'qf_ehea_levels = "{qf_ehea_level}"')

        if crossborder := request.query_params.get('crossborder', None):
            filters.append(f'crossborder = {BooleanExtendedField.to_internal_value(None, crossborder)}')

        if other_provider := request.query_params.get('other_provider', None):
            filters.append(f'is_other_provider = {BooleanExtendedField.to_internal_value(None, other_provider)}')

        return filters

    def convert_hit(self, r):
        # names
        if r['eter_id']:
            r['name_select_display'] = f"{r['name_primary']} ({r['eter_id']})"
        else:
            r['name_select_display'] = r['name_primary']
        for name in r['names']:
            if name['name_valid_to'] is None:
                r['name_official_display'] = name['name_official']
            else:
                name['name_valid_to'] = self.timestamp_to_isodate(name['name_valid_to'])
        if r['name_official_display'] != r['name_primary']:
            r['name_display'] = f"{r['name_official_display']} / {r['name_primary']}"
        else:
            r['name_display'] = r['name_primary']

        # QF-EHEA levels
        r['qf_ehea_level'] = r.pop("qf_ehea_levels")

        # relationships
        def convert_related(new_style):
            for rel in new_style:
                yield {
                    "deqar_id": rel['institution']['deqar_id'],
                    "eter_id": rel['institution']['eter_id'],
                    "name_primary": rel['institution']['name_primary'],
                    "website_link": rel['institution']['website_link'],
                    "relationship_type": rel['relationship_type'],
                    "valid_from": self.timestamp_to_isodate(rel['valid_from']),
                    "valid_to": self.timestamp_to_isodate(rel['valid_to']),
                }
        r['hierarchical_relationships'] = {
            "part_of":  list(convert_related(r.pop("part_of"))),
            "includes": list(convert_related(r.pop("includes"))),
        }

        # date formats
        r['founding_date'] = self.timestamp_to_isodate(r['founding_date'])
        r['closure_date'] = self.timestamp_to_isodate(r['closure_date'])
        r['date_created'] = self.timestamp_to_isodatetime(r.pop('created_at'))

        # merged country list
        countries = set()
        for l in r['locations']:
            countries.add(l['country']['name_english'])
        r["country"] = list(countries)

        # location
        r['place'] = r.pop("locations")
        for loc in r['place']:
            loc["country"] = loc['country']['name_english']
            loc["country_valid_from"] = self.timestamp_to_isodate(loc['country_valid_from'])
            loc["country_valid_to"] = self.timestamp_to_isodate(loc['country_valid_to'])


class InstitutionDetailByETER(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution (via ETER).
    """
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        try:
            return Institution.objects.get(eter_id=self.kwargs['eter_id'])
        except Institution.DoesNotExist:
            raise Http404


class InstitutionDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        try:
            return Institution.objects.get(pk=self.kwargs['pk'])
        except Institution.DoesNotExist:
            raise Http404


class InstitutionDetailByIdentifier(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution (via identifier).
    """
    serializer_class = InstitutionDetailSerializer

    def get_object(self):
        resource = self.kwargs.get('resource', None)
        identifier = self.kwargs.get('identifier', None)

        try:
            iid = InstitutionIdentifier.objects.filter(identifier=identifier, resource=resource)
            if iid:
                return iid.first().institution
            else:
                raise Http404
        except Institution.DoesNotExist:
            raise Http404


class InstitutionIdentifierResourcesList(generics.ListAPIView):
    """
        Returns all the identifier resources.
    """
    queryset = IdentifierResource.objects.filter(institutionidentifier__isnull=False).distinct()
    serializer_class = InstitutionResourceSerializer
    pagination_class = None
    ordering_fields = ('resource',)
    ordering = ('resource',)

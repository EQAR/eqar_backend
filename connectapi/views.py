from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters import rest_framework as filters, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from meilisearch.errors import MeilisearchApiError

from eqar_backend.xml_renderer import XMLRenderer
from eqar_backend.meilisearch import MeiliClient
from eqar_backend.serializer_fields.boolean_extended_serializer_field import BooleanExtendedField

from webapi.v2.views.meili_solr_view import MeiliSolrBackportView
from connectapi.europass.accrediation_xml_creator_v2 import AccrediationXMLCreatorV2

from agencies.models import AgencyESGActivity
from countries.models import Country
from institutions.models import Institution

from webapi.inspectors.report_search_inspector import ReportSearchInspector

from webapi.v2.serializers.agency_serializers import AgencyActivityDEQARConnectListSerializer
from webapi.v2.serializers.institution_serializers import InstitutionDEQARConnectListSerializer

from webapi.v2.views import institution_views


SEARCH_CHOICES = (
    ("locations.city", "city only"),
    ("website_link", "website URL"),
    ("deqar_id", "DEQARINST ID"),
    ("eter_id", "ETER ID"),
)

class InstitutionFilterClass(filters.FilterSet):
    query = filters.CharFilter(label='Search string')
    country = filters.ModelChoiceFilter(label='Country (ISO 3166-alpha2)', queryset=Country.objects.all(),
                                        to_field_name='iso_3166_alpha2')
    country_id = filters.ModelChoiceFilter(label='Country (DEQAR ID)', queryset=Country.objects.all(),
                                           to_field_name='id')
    search_field = filters.ChoiceFilter(label='Limit search field', choices=SEARCH_CHOICES)

    ordering = OrderingFilter(
        fields=(
            'score',
            'name_sort',
            'founding_date',
            'closure_date',
            'country',
            'deqar_id',
            'eter_id',
        ),
        field_labels={
            'score': "Relevance (text search)",
            'name_sort': "Alphabetical",
            'founding_date': "Founding date",
            'closure_date': "Closing date",
            'country': "Country (English name)",
            'deqar_id': "DEQARINST ID",
            'eter_id': "ETER ID",
        }
    )

class ProviderFilterClass(InstitutionFilterClass):
    other_provider = filters.BooleanFilter(label='Is other provider (false = higher education institution)')


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[ReportSearchInspector],
))
class ProviderDEQARConnectList(MeiliSolrBackportView):
    """
    Returns a list of all education providers existing in DEQAR.

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    queryset = Institution.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProviderFilterClass
    permission_classes = (permissions.AllowAny,)
    serializer_class = InstitutionDEQARConnectListSerializer

    MEILI_INDEX = 'INDEX_INSTITUTIONS'
    ORDERING_MAPPING = {
        'name_sort': 'name_sort',
        'founding_date': 'founding_date',
        'closure_date': 'closure_date',
        'country': 'locations.country.name_english',
        'deqar_id': 'deqar_id',
        'eter_id': 'eter_id',
    }
    FACET_NAMES = {
        'locations.country.id': 'country_facet',
        'is_other_provider': 'other_provider_facet',
    }
    FACET_LOOKUP = {
        'locations.country.id': { 'model': Country,           'attribute': 'name_english' },
    }

    def make_filters(self, request):
        filters = [ ]

        if country_id := self.lookup_object(Country, 'iso_3166_alpha2', 'country', 'id', 'country_id'):
            filters.append(f'locations.country.id = {country_id}')

        if other_provider := request.query_params.get('other_provider', None):
            filters.append(f'is_other_provider = {BooleanExtendedField.to_internal_value(None, other_provider)}')

        return filters


    def make_meili_params(self, request):
        return {
            "attributesToRetrieve": [
                "id",
                "deqar_id",
                "eter_id",
                "name_primary",
                "website_link",
                "is_other_provider",
                "organization_type",
                "names",
                "founding_date",
                "closure_date",
                "locations",
                "created_at",
                "part_of",
                "includes",
            ],
            "attributesToSearchOn": [ request.query_params.get('search_field', '*') or '*' ],
        }


    def convert_hit(self, r):
        # merged country list
        countries = set()
        cities = set()
        for l in r['locations']:
            countries.add(l['country']['name_english'])
            cities.add(l['city'])
        r["country"] = list(countries)
        r["city"] = list(cities)

        # date formats
        r['founding_date'] = self.timestamp_to_isodate(r['founding_date'])
        r['closure_date'] = self.timestamp_to_isodate(r['closure_date'])
        r['date_created'] = self.timestamp_to_isodatetime(r.pop('created_at'))
        for name in r['names']:
            name['name_valid_to'] = self.timestamp_to_isodate(name['name_valid_to'])
        for rel in r["part_of"]:
            rel["valid_from"] = self.timestamp_to_isodate(rel['valid_from'])
            rel["valid_to"] = self.timestamp_to_isodate(rel['valid_to'])
        for loc in r['locations']:
            loc["country_valid_from"] = self.timestamp_to_isodate(loc['country_valid_from'])
            loc["country_valid_to"] = self.timestamp_to_isodate(loc['country_valid_to'])


class InstitutionDEQARConnectList(ProviderDEQARConnectList):
    """
    Returns a list of all the higher education institutions existing in DEQAR.

    NB: This is a compatibility with for the legacy v2 view, originally based on Solr. It
    operates on the Meilisearch index and enriches the results to be fully compatible with
    the original v2 return format.
    """
    filterset_class = InstitutionFilterClass

    def make_filters(self, request):
        filters = super().make_filters(request)
        filters.append("is_other_provider = False")
        return filters


class InstitutionDetail(institution_views.InstitutionDetail):
    """
    Return full information on a single institution/other provider
    """
    permission_classes = (permissions.AllowAny,)

@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('eter_id', 'path', description='ETER ID (format: CCNNNN)', required=True, type=openapi.TYPE_STRING),
    ],
    responses={
        404: 'ETER ID could not be found',
    }
))
class InstitutionDetailByETER(institution_views.InstitutionDetailByETER):
    """
    Return full information on a single institution/other provider, identified by its ETER ID
    """
    permission_classes = (permissions.AllowAny,)

@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('resource', 'path', description='Identifier type (resource tag as used in DEQAR)', required=True, type=openapi.TYPE_STRING),
        openapi.Parameter('identifier', 'path', description='Identifier', required=True, type=openapi.TYPE_STRING),
    ],
    responses={
        404: 'Identifier could not be resolved found',
    }
))
class InstitutionDetailByIdentifier(institution_views.InstitutionDetailByIdentifier):
    """
    Return full information on a single institution/other provider, identified by an identifier known in DEQAR
    """
    permission_classes = (permissions.AllowAny,)

class InstitutionIdentifierResourcesList(institution_views.InstitutionIdentifierResourcesList):
    """
    Provide a list of identifier types
    """
    permission_classes = (permissions.AllowAny,)


class AgencyActivityDEQARConnectList(generics.ListAPIView):
    """
    Returns a list of the activities for each Agency where the user has the right to submit.
    """
    serializer_class = AgencyActivityDEQARConnectListSerializer

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency.submitting_agency.all()
        return AgencyESGActivity.objects.filter(agency__allowed_agency__in=submitting_agency)\
            .order_by('agency__acronym_primary')


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('country_code', 'path', description='Country code (ISO 3166-alpha2 or -alpha3)', required=True, type=openapi.TYPE_STRING),
    ],
    responses={
        200: 'DEQAR reports according to ELM application profile Accreditations (RDF+XML)',
        404: 'Country could not be found',
    }
))
class AccreditationXMLViewV2(APIView):
    permission_classes = []
    renderer_classes = (XMLRenderer,)

    def get(self, request, *args, **kwargs):
        country_code = self.kwargs['country_code']
        country = get_object_or_404(
            Country, Q(iso_3166_alpha3=country_code.upper()) | Q(iso_3166_alpha2__exact=country_code)
        )
        creator = AccrediationXMLCreatorV2(country, request)
        return Response(creator.create(), content_type='application/xml')

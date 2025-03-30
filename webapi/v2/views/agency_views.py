import datetime
from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters

from agencies.models import Agency, AgencyEQARDecision, AgencyESGActivity, AgencyActivityGroup
from webapi.inspectors.agency_list_inspector import AgencyListInspector
from webapi.v2.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer, \
    AgencyListByFocusCountrySerializer, AgencyEQARDecisionListSerializer, \
    AgencyActivityGroupListSerializer, \
    AgencyActivityDEQARConnectListSerializer

AGENCY_REGISTERED_CHOICES = (
    ('True', 'True'),
    ('False', 'False'),
    ('All', 'All'),
)


class AgencyFilterClass(filters.FilterSet):
    """
        Filter class for Agency List filtering...
    """
    registered = filters.ChoiceFilter(label='Is Registered', method='filter_registered',
                                      choices=AGENCY_REGISTERED_CHOICES)

    def filter_registered(self, queryset, name, value):
        if value == 'True':
            queryset = Agency.objects.filter(is_registered=True)
        elif value == 'False':
            queryset = Agency.objects.filter(is_registered=False)
        elif value == 'All':
            queryset = Agency.objects.all()
        return queryset


@method_decorator(name='get', decorator=swagger_auto_schema(
   filter_inspectors=[AgencyListInspector],
))
class AgencyList(generics.ListAPIView):
    """
        Returns a list of all the agencies in DEQAR.
    """
    queryset = Agency.objects.filter(is_registered=True)
    serializer_class = AgencyListSerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    filterset_class = AgencyFilterClass
    ordering_fields = ('name_primary', 'acronym_primary')
    ordering = ('acronym_primary', 'name_primary')


class AgencyListByFocusCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR operating in the submitted country.
    """
    serializer_class = AgencyListByFocusCountrySerializer
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_context(self):
        context = super(AgencyListByFocusCountry, self).get_serializer_context()
        if 'country' in self.kwargs:
            context['country_id'] = self.kwargs['country']
        return context

    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return Agency.objects.filter(Q(agencyfocuscountry__country=self.kwargs['country']))
        else:
            return Agency.objects.filter(
                Q(agencyfocuscountry__country=self.kwargs['country']) & (
                    Q(agencyfocuscountry__country_valid_to__isnull=True) |
                    Q(agencyfocuscountry__country_valid_to__gte=datetime.datetime.now())
                )
            )

    def get_paginated_response(self, data):
        data = sorted(data, key=lambda d: (
                -d['is_registered'],
                -d['country_is_official'],
                d['acronym_primary'],
                d['name_primary']
        ))
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class AgencyListByOriginCountry(AgencyList):
    """
        Returns a list of all the agencies in DEQAR based in the submitted country.
    """
    def get_queryset(self):
        include_history = self.request.query_params.get('history', None)

        if include_history == 'true':
            return Agency.objects.filter(Q(country=self.kwargs['country']))
        else:
            return Agency.objects.filter(
                Q(country=self.kwargs['country']) & Q(is_registered=True)
            )


class AgencyDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected agency.
    """
    queryset = Agency.objects.all()
    serializer_class = AgencyDetailSerializer


class AgencyDecisionList(generics.ListAPIView):
    """
        Returns all the EQAR decisions in chronological order.
    """
    queryset = AgencyEQARDecision.objects.all().order_by('-decision_date', 'agency__acronym_primary')
    serializer_class = AgencyEQARDecisionListSerializer
    pagination_class = None


class AgencyActivityList(generics.ListAPIView):
    """
    Returns a list of all ESG activities
    """
    serializer_class = AgencyActivityDEQARConnectListSerializer
    queryset = AgencyESGActivity.objects.all()


class AgencyActivityGroupList(generics.ListAPIView):
    """
    Returns a list of all ESG activity groups
    """
    serializer_class = AgencyActivityGroupListSerializer
    queryset = AgencyActivityGroup.objects.all()
    pagination_class = None


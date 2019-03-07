import datetime

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from adminapi.serializers.select_serializers import AgencyESGActivitySerializer
from agencies.models import Agency, AgencyActivityType, AgencyProxy, AgencyESGActivity


class AgencyESGActivityFilterClass(filters.FilterSet):
    agency = filters.ModelChoiceFilter(field_name='agency', queryset=Agency.objects.all())
    activity = filters.CharFilter(label='Activity', method='search_activity')
    activity_type = filters.ModelChoiceFilter(field_name='activity_type', queryset=AgencyActivityType.objects.all())

    def search_activity(self, queryset, name, value):
        return queryset.filter(activity__icontains=value)

    class Meta:
        model = AgencyESGActivity
        fields = ['agency', 'activity', 'activity_type']


class AgencyESGActivityList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering = ('agency', 'activity')
    filter_class = AgencyESGActivityFilterClass

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        agency_proxies = AgencyProxy.objects.filter(
            Q(submitting_agency=submitting_agency) &
            (Q(proxy_to__gte=datetime.date.today()) | Q(proxy_to__isnull=True)))
        agencies = Agency.objects.filter(allowed_agency__in=agency_proxies).order_by('acronym_primary')
        return AgencyESGActivity.objects.filter(agency__in=agencies).order_by('agency', 'activity')
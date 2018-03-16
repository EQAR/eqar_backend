from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.serializers.report_serializer import ReportDashboardSerializer
from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report


class ReportsByAgency(ListAPIView):
    serializer_class = ReportDashboardSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('id', 'name')
    ordering = ('-id', 'name')

    def get_queryset(self):
        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        ap = submitting_agency.submitting_agency.all()
        reports = Report.objects.filter(agency__allowed_agency__in=ap)
        return reports


class DashboardBadgesView(APIView):
    def get(self, request):
        counters = {}

        user = self.request.user
        submitting_agency = user.deqarprofile.submitting_agency
        ap = submitting_agency.submitting_agency.all()
        reports = Report.objects.filter(agency__allowed_agency__in=ap)

        counters['reports_total'] = reports.count()
        counters['high_level_flags_total'] = reports.filter(flag=3).count()
        counters['institutions_total'] = Institution.objects.filter(reports__in=reports).count()
        counters['programmes_total'] = Programme.objects.filter(report__in=reports).count()

        return Response(counters)
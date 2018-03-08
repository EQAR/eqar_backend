from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from adminapi.serializers.report_serializer import ReportDashboardSerializer
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

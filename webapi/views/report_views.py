from django.db.models.expressions import RawSQL
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from reports.models import Report
from webapi.serializers.report_serializers import ReportListSerializer, ReportDetailSerializer


class ReportListByAgency(generics.ListAPIView):
    """
        Returns a list of all the reports which were submitted to DEQAR filtered by agency.
    """
    serializer_class = ReportListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('valid_from',)
    ordering = ('institution_name_primary', 'programme_name_primary')

    def get_queryset(self):
        agency_id = self.kwargs['agency']
        qs = Report.objects.extra(
            select={
                'institution_id': 'deqar_reports_institutions.institution_id',
                'institution_name_primary': 'deqar_institutions.name_primary',
                'programme_id': 'deqar_programmes.id',
                'programme_name_primary': 'deqar_programmes.name_primary'
            },
            tables=["deqar_programmes", "deqar_reports_institutions", "deqar_institutions"],
            where=["deqar_reports.id = deqar_programmes.report_id AND "
                   "deqar_reports.id = deqar_reports_institutions.report_id AND "
                   "deqar_reports_institutions.institution_id = deqar_institutions.id"]
        )
        return qs.filter(agency_id=agency_id)


class ReportListByInstitution(generics.ListAPIView):
    """
        Returns a list of all the reports which were submitted to DEQAR filtered by institution.
    """
    serializer_class = ReportListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('valid_to', 'programme_name_primary')
    ordering = ('institution_name_primary', 'programme_name_primary')

    def get_queryset(self):
        institution_id = self.kwargs['institution']
        qs = Report.objects.extra(
            select={
                'institution_id': 'deqar_reports_institutions.institution_id',
                'institution_name_primary': 'deqar_institutions.name_primary',
                'programme_id': 'deqar_programmes.id',
                'programme_name_primary': 'deqar_programmes.name_primary'
            },
            tables=["deqar_programmes", "deqar_reports_institutions", "deqar_institutions"],
            where=["deqar_reports.id = deqar_programmes.report_id AND "
                   "deqar_reports.id = deqar_reports_institutions.report_id AND "
                   "deqar_reports_institutions.institution_id = deqar_institutions.id AND "
                   "institution_id = %s"],
            params=[institution_id]
        )
        return qs


class ReportListByCountry(generics.ListAPIView):
    """
        Returns a list of all the reports which were submitted to DEQAR filtered by country.
    """
    serializer_class = ReportListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('valid_to', 'agency')
    ordering = ('institution_name_primary', 'programme_name_primary')

    def get_queryset(self):
        country_id = self.kwargs['country']
        qs = Report.objects.extra(
            select={
                'institution_id': 'deqar_reports_institutions.institution_id',
                'institution_name_primary': 'deqar_institutions.name_primary',
                'programme_id': 'deqar_programmes.id',
                'programme_name_primary': 'deqar_programmes.name_primary'
            },
            tables=["deqar_programmes",
                    "deqar_programmes_countries",
                    "deqar_reports_institutions",
                    "deqar_institutions",
                    "deqar_institution_countries"],
            where=["deqar_reports.id = deqar_programmes.report_id AND "
                   "deqar_reports.id = deqar_reports_institutions.report_id AND "
                   "deqar_reports_institutions.institution_id = deqar_institutions.id AND "
                   "deqar_institutions.id = deqar_institution_countries.institution_id AND "
                   "deqar_programmes.id = deqar_programmes_countries.programme_id AND "
                   "(deqar_institution_countries.country_id = %s OR "
                   "deqar_programmes_countries.country_id = %s)"
                   ],
            params=[country_id, country_id]
        )
        return qs


class ReportDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected report.
    """
    queryset = Report.objects.all()
    serializer_class = ReportDetailSerializer
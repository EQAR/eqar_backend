import datetime

from datedelta import datedelta
from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404

from institutions.models import Institution
from reports.models import Report
from webapi.v2.serializers.report_detail_serializers import ReportDetailSerializer


class ReportListByInstitution(generics.ListAPIView):
    """
        Returns a list of all the institutional level reports which were submitted to DEQAR filtered by institution.
    """
    serializer_class = ReportDetailSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'agency')
    ordering = ('name', 'agency')

    def get_serializer_context(self):
        context = super(ReportListByInstitution, self).get_serializer_context()

        if 'institution' in self.kwargs:
            institution = get_object_or_404(Institution, pk=self.kwargs['institution'])
        else:
            return context

        context['institution'] = institution
        context['report_type'] = 'institutional'
        return context

    def get_queryset(self):
        include_history = self.request.query_params.get('history', 'true')
        institution = get_object_or_404(Institution, pk=self.kwargs['institution'])
        report_type = self.kwargs.get('report_type', None)
        programme_is_null = False if report_type == 'programme' else True

        if report_type == 'programme':
            filter = Q(agency_esg_activities__activity_group__activity_type=1) | \
                     Q(agency_esg_activities__activity_group__activity_type=3) | \
                     Q(agency_esg_activities__activity_group__activity_type=4)
        else:
            filter = Q(agency_esg_activities__activity_group__activity_type=2) | \
                     Q(agency_esg_activities__activity_group__activity_type=4)

        # Add Original
        if include_history == 'true':
            qs = Report.objects.filter(Q(institutions__in=[institution]) | Q(platforms__in=[institution])).filter(filter).filter(~Q(flag=3))
        else:
            qs = Report.objects.filter(Q(institutions__in=[institution]) | Q(platforms__in=[institution])).filter(filter).filter(~Q(flag=3)).filter(
                Q(valid_to__gte=datetime.datetime.now()) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=datetime.datetime.now() - datedelta(years=6))
                )
            )

        # Add Hierarchical Relationship
        institution_ids = []

        # Add Children
        for inst in institution.relationship_parent.exclude(relationship_type__type='educational platform'):
            institution_ids.append(inst.institution_child_id)

        # Add Parents
        for inst in institution.relationship_child.exclude(relationship_type__type='educational platform'):
            institution_ids.append(inst.institution_parent_id)

        if len(institution_ids) > 0:
            if include_history == 'true':
                qs_h = Report.objects.filter(Q(institutions__id__in=institution_ids)).filter(filter).filter(~Q(flag=3))
            else:
                qs_h = Report.objects.filter(Q(institutions__id__in=institution_ids)).filter(filter).filter(~Q(flag=3))\
                    .filter(
                        Q(valid_to__gte=datetime.datetime.now()) | (
                                Q(valid_to__isnull=True) &
                                Q(valid_from__gte=datetime.datetime.now() - datedelta(years=6))
                        )
                    )
            qs = qs | qs_h

        # Succeeding target
        for inst_rel in institution.relationship_target.filter(relationship_type=2):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(Q(institutions__in=institution_source)).filter(filter).filter(~Q(flag=3))\
                .filter(
                    (
                        Q(valid_from__lte=event_date) &
                        Q(valid_to__gte=event_date)
                    ) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=event_date - datedelta(years=6))
                    )
                )
            qs = qs | qs_h

        # Absorbing source
        for inst_rel in institution.relationship_source.filter(relationship_type=3):
            institution_source = [inst_rel.institution_target]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(Q(institutions__in=institution_source)).filter(filter).filter(~Q(flag=3))\
                .filter(
                    (
                        Q(valid_from__lte=event_date) &
                        Q(valid_to__gte=event_date)
                    ) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=event_date - datedelta(years=6))
                    )
                )
            qs = qs | qs_h

        # Spun off target
        for inst_rel in institution.relationship_target.filter(relationship_type=4):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(Q(institutions__in=institution_source)).filter(filter).filter(~Q(flag=3))\
                .filter(
                    (
                        Q(valid_from__lte=event_date) &
                        Q(valid_to__gte=event_date)
                    ) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=event_date - datedelta(years=6))
                    )
                )
            qs = qs | qs_h

        qs = qs.prefetch_related('reportfile_set')
        return qs.distinct()


class ReportDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    serializer_class = ReportDetailSerializer
    queryset = Report.objects.all()

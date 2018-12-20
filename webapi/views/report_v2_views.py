import datetime

from datedelta import datedelta
from django.db.models import Q, Case, When, Value, CharField, F
from django.db.models.functions import Concat
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404

from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report
from webapi.serializers.programme_v2_serializers import ProgrammeSerializer
from webapi.serializers.report_v2_serializers import ReportSerializer


class ReportProgrammeListByInstitution(generics.ListAPIView):
    """
        Returns a list of all the programme level reports which were submitted to DEQAR filtered by institution.
    """
    serializer_class = ProgrammeSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name_primary',)
    ordering = ('name_primary',)

    def get_serializer_context(self):
        context = super(ReportProgrammeListByInstitution, self).get_serializer_context()

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

        # Add Original
        if include_history == 'true':
            qs = Programme.objects.filter(
                Q(report__institutions__in=[institution]) & ~Q(report__flag=3)
            )
        else:
            qs = Programme.objects.filter(
                Q(report__institutions__in=[institution]) & ~Q(report__flag=3) &
                (
                    Q(report__valid_to__gte=datetime.datetime.now()) | (
                        Q(report__valid_to__isnull=True) &
                        Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )

        # Hierarchical Relationships
        institution_ids = []

        # Add Children
        for inst in institution.relationship_parent.all():
            institution_ids.append(inst.institution_child_id)

        # Add Parents
        for inst in institution.relationship_child.all():
            institution_ids.append(inst.institution_parent_id)

        if len(institution_ids) > 0:
            if include_history == 'true':
                qs_h = Programme.objects.filter(
                    Q(report__institutions__id__in=institution_ids) & ~Q(report__flag=3)
                )
            else:
                qs_h = Programme.objects.filter(
                    Q(report__institutions__id__in=institution_ids) & ~Q(report__flag=3) &
                    (
                        Q(report__valid_to__gte=datetime.datetime.now()) | (
                            Q(report__valid_to__isnull=True) &
                            Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                        )
                    )
                )
            qs = qs | qs_h

        # Succeeding target
        for inst_rel in institution.relationship_target.filter(relationship_type=2):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Programme.objects.filter(
                Q(report__institutions__in=institution_source) & ~Q(report__flag=3) &
                (
                    Q(report__valid_to__gte=event_date) | (
                        Q(report__valid_to__isnull=True) &
                        Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        # Absorbing source
        for inst_rel in institution.relationship_source.filter(relationship_type=2):
            institution_source = [inst_rel.institution_target]
            event_date = inst_rel.relationship_date
            qs_h = Programme.objects.filter(
                Q(report__institutions__in=institution_source) & ~Q(report__flag=3) &
                (
                    Q(report__valid_to__gte=event_date) | (
                        Q(report__valid_to__isnull=True) &
                        Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        # Spun off target
        for inst_rel in institution.relationship_target.filter(relationship_type=4):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Programme.objects.filter(
                Q(report__institutions__in=institution_source) & ~Q(report__flag=3) &
                (
                    Q(report__valid_to__gte=event_date) | (
                        Q(report__valid_to__isnull=True) &
                        Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        qs = qs.select_related('report', 'report__agency', 'report__status', 'report__decision')
        qs = qs.prefetch_related('programmename_set', 'programmeidentifier_set', 'countries')
        return qs.distinct()


class ReportInstitutionListByInstitution(generics.ListAPIView):
    """
        Returns a list of all the institutional level reports which were submitted to DEQAR filtered by institution.
    """
    serializer_class = ReportSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'agency')
    ordering = ('name', 'agency')

    def get_serializer_context(self):
        context = super(ReportInstitutionListByInstitution, self).get_serializer_context()

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

        # Add Original
        if include_history == 'true':
            qs = Report.objects.filter(
                Q(institutions__in=[institution]) & Q(programme__isnull=True) & ~Q(flag=3)
            )
        else:
            qs = Report.objects.filter(
                Q(institutions__id__in=[institution]) & Q(programme__isnull=True) & ~Q(flag=3) &
                (
                    Q(valid_to__gte=datetime.datetime.now()) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )

        # Add Hierarchical Relationship
        institution_ids = []

        # Add Children
        for inst in institution.relationship_parent.all():
            institution_ids.append(inst.institution_child_id)

        # Add Parents
        for inst in institution.relationship_child.all():
            institution_ids.append(inst.institution_parent_id)

        if len(institution_ids) > 0:
            if include_history == 'true':
                qs_h = Report.objects.filter(
                    Q(institutions__id__in=institution_ids) & Q(programme__isnull=True) & ~Q(flag=3)
                )
            else:
                qs_h = Report.objects.filter(
                    Q(institutions__id__in=institution_ids) & Q(programme__isnull=True) & ~Q(flag=3) &
                    (
                        Q(valid_to__gte=datetime.datetime.now()) | (
                            Q(valid_to__isnull=True) &
                            Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                        )
                    )
                )
            qs = qs | qs_h

        # Succeeding target
        for inst_rel in institution.relationship_target.filter(relationship_type=2):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(
                Q(institutions__in=institution_source) & Q(programme__isnull=True) & ~Q(flag=3) &
                (
                    Q(valid_to__gte=event_date) | (
                        Q(valid_to__isnull=True) & Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        # Absorbing source
        for inst_rel in institution.relationship_source.filter(relationship_type=3):
            institution_source = [inst_rel.institution_target]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(
                Q(institutions__in=institution_source) & Q(programme__isnull=True) & ~Q(flag=3) &
                (
                    Q(valid_to__gte=event_date) | (
                        Q(valid_to__isnull=True) & Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        # Spun off target
        for inst_rel in institution.relationship_target.filter(relationship_type=4):
            institution_source = [inst_rel.institution_source]
            event_date = inst_rel.relationship_date
            qs_h = Report.objects.filter(
                Q(institutions__in=institution_source) & Q(programme__isnull=True) & ~Q(flag=3) &
                (
                    Q(valid_to__gte=event_date) | (
                        Q(valid_to__isnull=True) & Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
            qs = qs | qs_h

        qs = qs.prefetch_related('reportfile_set')
        return qs.distinct()

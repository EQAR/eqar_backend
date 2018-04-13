import datetime

from datedelta import datedelta
from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report
from webapi.serializers.programme_serializers import ProgrammeSerializer
from webapi.serializers.report_serializers import ReportSerializer


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
        parents = []
        children = []
        institution = Institution.objects.get(pk=self.kwargs['institution'])

        # Children
        for inst in institution.relationship_parent.all():
            children.append(inst.institution_child_id)

        # Parents
        for inst in institution.relationship_child.all():
            parents.append(inst.institution_parent_id)

        context['institution'] = institution.id
        context['children'] = children
        context['parents'] = parents
        return context

    def get_queryset(self):
        include_history = self.request.query_params.get('history', 'true')
        institution = Institution.objects.get(pk=self.kwargs['institution'])
        institution_ids = [institution.id]

        # Add Children
        for inst in institution.relationship_parent.all():
            institution_ids.append(inst.institution_child_id)

        # Add Parents
        for inst in institution.relationship_child.all():
            institution_ids.append(inst.institution_parent_id)

        if include_history == 'true':
            qs = Programme.objects.filter(
                Q(report__institutions__id__in=institution_ids) & ~Q(report__flag=3)
            ).distinct()
        else:
            qs = Programme.objects.filter(
                Q(report__institutions__id__in=institution_ids) & ~Q(report__flag=3) &
                (
                    Q(report__valid_to__gte=datetime.datetime.now()) | (
                        Q(report__valid_to__isnull=True) &
                        Q(report__valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            ).distinct()
        qs = qs.select_related('report', 'report__agency', 'report__status', 'report__decision')
        qs = qs.prefetch_related('programmename_set', 'programmeidentifier_set', 'countries')
        return qs


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
        parents = []
        children = []
        institution = Institution.objects.get(pk=self.kwargs['institution'])

        # Children
        for inst in institution.relationship_parent.all():
            children.append(inst.institution_child_id)

        # Parents
        for inst in institution.relationship_child.all():
            parents.append(inst.institution_parent_id)

        context['institution'] = institution.id
        context['children'] = children
        context['parents'] = parents
        return context

    def get_queryset(self):
        include_history = self.request.query_params.get('history', 'true')
        institution = Institution.objects.get(pk=self.kwargs['institution'])
        institution_ids = [institution.id]

        # Add Children
        for inst in institution.relationship_parent.all():
            institution_ids.append(inst.institution_child_id)

        # Add Parents
        for inst in institution.relationship_child.all():
            institution_ids.append(inst.institution_parent_id)

        if include_history == 'true':
            qs = Report.objects.filter(
                Q(institutions__id__in=institution_ids) & Q(programme__isnull=True)
            )
        else:
            qs = Report.objects.filter(
                Q(institutions__id__in=institution_ids) & Q(programme__isnull=True) &
                (
                    Q(valid_to__gte=datetime.datetime.now()) | (
                        Q(valid_to__isnull=True) &
                        Q(valid_from__gte=datetime.datetime.now()-datedelta(years=6))
                    )
                )
            )
        qs = qs.prefetch_related('reportfile_set')
        return qs
from django.db.models import Q

from reports.models import Report


class ReportDuplicationChecker():
    def __init__(self, report):
        self.report = report

    def check(self):
        filters = Q()

        # Check for simple field values
        filters.add(Q(**{'valid_from': str(self.report.valid_from)}), Q.AND)
        filters.add(Q(**{'valid_to': str(self.report.valid_to)}), Q.AND)
        filters.add(Q(**{'decision__id': self.report.decision.id}), Q.AND)

        # Check institutions
        for institution in self.report.institutions.all():
            filters.add(Q(**{'institutions__id': institution.id}), Q.AND)

        # Check activities
        for activity in self.report.agency_esg_activities.all():
            filters.add(Q(**{'agency_esg_activities__id': activity.id}), Q.AND)

        # Check programme data
        for programme in self.report.programme_set.all():
            filters.add(Q(**{'programme__name_primary': programme.name_primary}), Q.AND)
            filters.add(Q(**{'programme__qf_ehea_level__id': programme.qf_ehea_level.id}), Q.AND)
            filters.add(Q(**{'programme__workload_ects': programme.workload_ects}), Q.AND)

        possible_duplications = Report.objects.filter(filters).exclude(id=self.report.id).count()

        if possible_duplications > 0:
            return True
        else:
            return False
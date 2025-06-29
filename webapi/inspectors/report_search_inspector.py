from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, DrfAPICompatInspector

from reports.models import ReportStatus, ReportDecision
from lists.models import QFEHEALevel
from agencies.models import AgencyActivityType


class ReportSearchInspector(DrfAPICompatInspector):
    enums = {
        'status': {
            'queryset': ReportStatus.objects.all(),
            'field': 'status',
        },
        'decision': {
            'queryset': ReportDecision.objects.all(),
            'field': 'decision',
        },
        'qf_ehea_level': {
            'queryset': QFEHEALevel.objects.all(),
            'field': 'level',
        },
        'activity_type': {
            'queryset': AgencyActivityType.objects.all(),
            'field': 'type',
        },
    }
    booleans = (
        'cross_border',
        'crossborder',
        'degree_outcome',
        'other_provider',
        'other_provider_covered',
    )
    dates = (
        'valid_on',
    )

    def get_filter_parameters(self, filter_backend):
        results = super(ReportSearchInspector, self).get_filter_parameters(filter_backend)

        if isinstance(filter_backend, DjangoFilterBackend) and results != NotHandled:
            for param in results:
                if 'name' in param:
                    if param['name'] in self.enums:
                        param.enum = [ getattr(obj, self.enums[param['name']]['field']) for obj in self.enums[param['name']]['queryset'] ]
                    elif param['name'] in self.booleans:
                        param['type'] = 'boolean'
                    elif param['name'] in self.dates:
                        param['format'] = 'date'

        return results


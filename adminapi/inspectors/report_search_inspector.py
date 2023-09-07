from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, CoreAPICompatInspector


class ReportSearchInspector(CoreAPICompatInspector):
    fields = {
        'query': {
            'description': 'Search string to search in institution and programme names, countries and cities.',
            'type': 'string'
        },
        'agency': {
            'description': 'Acronym of an agency. The resultset contains reports, '
                           'submitted by the name the agency.',
            'type': 'string'
        },
        'country': {
            'description': 'Name of a country. The resultset contains reports submitted for an institution located '
                           'in the selected countries or'
                           'for a programme (from a report) was listed in the submitted country.',
            'type': 'string'
        },
        'activity': {
            'description': 'Name of an activity. The resultset contains reports submitted under the defined activity.',
            'type': 'string'
        },
        'activity_type': {
            'description': 'Name of an activity type. The resultset contains reports submitted '
                           'under the defined activity type.',
            'type': 'string'
        },
        'status': {
            'description': 'Name of an agency status. The resultset contains reports '
                           'submitted by agencies with the defined status.',
            'type': 'string'
        },
        'active': {
            'description': 'Shows only reports, which are currently valid.',
            'type': 'boolean'
        },
        'year': {
            'description': 'Shows only reports, which were valid in the written year.',
            'type': 'string'
        },
        'alternative_provider_covered': {
            'description': 'Shows only reports, which are covering at least one organisation which is alternative '
                           'provider.',
            'type': 'boolean'
        },
        'micro_credentials_covered': {
            'description': 'Shows only reports, which are covering micro credentials.',
            'type': 'boolean'
        },
        'degree_outcome': {
            'description': 'Shows programme reports, where degree outcome is full degree.',
            'type': 'boolean'
        },
        'ordering': {
            'description': 'Definition of the resultset ordering.',
            'type': 'string',
            'enum': ['institution_programme_sort', '-institution_programme_sort',
                     'agency', '-agency',
                     'country', '-country',
                     'activity', '-activity',
                     'valid_from', '-valid_from',
                     'flag', '-flag',
                     'score', '-score']
        }
    }

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(ReportSearchInspector, self).get_filter_parameters(filter_backend)
            for param in results:
                for field, config in self.fields.items():
                    if param.get('name') == field:
                        if 'description' in config.keys():
                            param.description = config['description']
                        if 'type' in config.keys():
                            param.type = config['type']
                        if 'enum' in config.keys():
                            param.enum = config['enum']
            return results

        if isinstance(filter_backend, OrderingFilter):
            results = super(ReportSearchInspector, self).get_filter_parameters(filter_backend)
            return results

        return NotHandled

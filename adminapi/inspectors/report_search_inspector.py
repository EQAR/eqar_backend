from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, CoreAPICompatInspector


class ReportSearchInspector(CoreAPICompatInspector):
    fields = {
        'query': {
            'description': 'Search string to search in institution names, countries and cities.',
            'type': 'string'
        },
        'agency': {
            'description': 'Acronym of an agency. The resultset contains institutions, '
                           'about which agencies were submitting reports.',
            'type': 'string'
        },
        'country': {
            'description': 'Name of a country. The resultset contains institutions located in the selected countries or'
                           'a programme (from a report) was listed in the submitted country.',
            'type': 'string'
        },
        'activity_type': {
            'description': 'Activity type, under the report was submitted.',
            'type': 'string'
        },
        'flag': {
            'description': 'Flag level raised after ingest.',
            'type': 'string'
        },
        'active': {
            'description': 'Shows only reports, which are currently active.',
            'type': 'boolean'
        },
        'year': {
            'description': 'Shows only reports, which were active in the written year.',
            'type': 'string'
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

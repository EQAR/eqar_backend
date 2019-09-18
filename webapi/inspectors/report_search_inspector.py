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
        'agency_id': {
            'description': 'ID of an agency. The resultset contains reports, '
                           'submitted by the name of the agency.',
            'type': 'string'
        },
        'country': {
            'description': 'Name of a country. The resultset contains reports submitted for an institution located '
                           'in the selected countries or'
                           'for a programme (from a report) was listed in the submitted country.',
            'type': 'string'
        },
        'country_id': {
            'description': 'ID of a country.  The resultset contains reports submitted for an institution located '
                           'in the selected countries or'
                           'for a programme (from a report) was listed in the submitted country.',
            'type': 'integer'
        },
        'activity': {
            'description': 'Name of an activity. The resultset contains reports submitted under the defined activity.',
            'type': 'string'
        },
        'activity_id': {
            'description': 'ID of an activity. The resultset contains reports submitted under the defined activity.',
            'type': 'integer'
        },
        'activity_type': {
            'description': 'Name of an activity type. The resultset contains reports submitted '
                           'under the defined activity type.',
            'type': 'string'
        },
        'activity_type_id': {
            'description': 'ID of an activity type. The resultset contains reports submitted '
                           'under the defined activity type.',
            'type': 'integer'
        },
        'status': {
            'description': 'Name of an agency status. The resultset contains reports '
                           'submitted by agencies with the defined status.',
            'type': 'string'
        },
        'status_id': {
            'description': 'ID of an agency status. The resultset contains reports '
                           'submitted by agencies with the defined status.',
            'type': 'integer'
        },
        'decision': {
            'description': 'Name of an EQAR decision. The resultset contains reports '
                           'submitted with the defined EQAR decision.',
            'type': 'string'
        },
        'decision_id': {
            'description': 'ID of an agency status. The resultset contains reports '
                           'submitted with the defined EQAR decision.',
            'type': 'integer'
        },
        'language': {
            'description': 'Name of a language. The resultset contains reports '
                           'submitted in the defined language.',
            'type': 'string'
        },
        'language_id': {
            'description': 'ID of an language. The resultset contains reports '
                           'submitted in the defined language.',
            'type': 'integer'
        },
        'crossborder': {
            'description': 'Boolean indicator if the report was submitted by an agency, which operates as a '
                           'crossborder agency in the institutions country.',
            'type': 'boolean'
        },
        'active': {
            'description': 'Shows only reports, which are currently valid.',
            'type': 'boolean'
        },
        'year': {
            'description': 'Shows only reports, which were valid in the written year.',
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

from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, CoreAPICompatInspector


class InstitutionSearchInspector(CoreAPICompatInspector):
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
        'agency_id': {
            'description': 'ID of an agency. The resultset contains institutions, '
                           'about which agencies were submitting reports.',
            'type': 'string'
        },
        'country': {
            'description': 'Name of a country. The resultset contains institutions located in the selected countries or'
                           ' a programme (from a report) was listed in the submitted country.',
            'type': 'string'
        },
        'country_id': {
            'description': 'ID of a country. The resultset contains institutions located in the selected countries or'
                           'a programme (from a report) was listed in the submitted country.',
            'type': 'integer'
        },
        'activity': {
            'description': 'Name of an activity. The resultset contains institutions about which reports were submitted'
                           'under the defined activity.',
            'type': 'string'
        },
        'activity_id': {
            'description': 'ID of an activity. The resultset contains institutions about which reports were submitted'
                           'under the defined activity.',
            'type': 'integer'
        },
        'activity_type': {
            'description': 'Name of an activity type. The resultset contains institutions about which reports '
                           'were submitted under the defined activity type.',
            'type': 'string'
        },
        'activity_type_id': {
            'description': 'ID of an activity type. The resultset contains institutions about which reports '
                           'were submitted under the defined activity type.',
            'type': 'integer'
        },
        'status': {
            'description': 'Name of an agency status. The resultset contains institutions about which reports '
                           'were submitted by agencies with the defined status.',
            'type': 'string'
        },
        'status_id': {
            'description': 'ID of an agency status. The resultset contains institutions about which reports '
                           'were submitted by agencies with the defined status.',
            'type': 'integer'
        },
        'qf_ehea_level': {
            'description': 'Name of the QF EHEA Level. The resultset contains institutions (with reports) with '
                           'the specified QF EHEA Level.',
            'type': 'string'
        },
        'qf_ehea_level_id': {
            'description': 'ID of the QF EHEA Level. The resultset contains institutions (with reports) with '
                           'the specified QF EHEA Level.',
            'type': 'integer'
        },
        'crossborder': {
            'description': 'Boolean indicator if an institution has a report by an agency, which operates as a '
                           'crossborder agency in the institutions country.',
            'type': 'boolean'
        },
        'ordering': {
            'description': 'Definition of the resultset ordering.',
            'type': 'string',
            'enum': ['name', '-name', 'score', '-score']
        }
    }

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(InstitutionSearchInspector, self).get_filter_parameters(filter_backend)
            if results != NotHandled:
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
            results = super(InstitutionSearchInspector, self).get_filter_parameters(filter_backend)
            return results

        return NotHandled

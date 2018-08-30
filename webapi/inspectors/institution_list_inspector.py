from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, CoreAPICompatInspector


class InstitutionListInspector(CoreAPICompatInspector):
    fields = {
        'history': {
            'description': 'Include historic records',
            'type': 'boolean'
        },
        'query': {
            'description': 'Search string to search in institution names, countries and cities.',
            'type': 'string'
        },
        'agency': {
            'description': 'ID of an agency. The resultset contains institutions, '
                            'about which agencies were submitting reports.',
            'type': 'integer'
        },
        'esg_activity': {
            'description': 'The identifier of the ESG Activity of the Agency.',
            'type': 'integer'
        },
        'country': {
            'description': 'ID of a country. The resultset contains institutions located in the selected countries or '
                            'a programme (from a report) was listed in the submitted country.',
            'type': 'integer'
        },
        'qf_ehea_level': {
            'description': 'ID of a QF EHEA Level record. The resultset contains institutions where the QF EHEA level '
                            'were set to the submitted value. '
                            'Values are: 1 - short cycle, 2 - first cycle, 3 - second cycle, 4 - third cycle',
            'type': 'integer',
            'enum': [1, 2, 3, 4]
        },
        'status': {
            'description': 'ID of the Report Status record. The resultset contains institutions where the connecting '
                            'reports were submitted with the value. '
                            'Values are: 1 - part of obligatory EQA system, 2 - voluntary',
            'type': 'integer',
            'enum': [1, 2]
        },
        'report_year': {
            'description': 'Year of the report. The resultset contains institutions where the connecting reports are '
                            'valid in the submitted year.',
            'type': 'integer'
        },
        'focus_country_is_crossborder': {
            'description': 'The resultset contains institutions where one of the focus countries are set '
                            'as cross boarder country.',
            'type': 'boolean'
        }
    }

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(InstitutionListInspector, self).get_filter_parameters(filter_backend)
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
            results = super(InstitutionListInspector, self).get_filter_parameters(filter_backend)
            return results

        return NotHandled
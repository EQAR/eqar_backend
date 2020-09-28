from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import NotHandled, CoreAPICompatInspector


class InstitutionSearchInspector(CoreAPICompatInspector):
    fields = {
        'query': {
            'description': 'Search string to search in institution names, countries and cities.',
            'type': 'string'
        },
        'country': {
            'description': 'Name of a country. The resultset contains institutions located in the selected country.',
            'type': 'string'
        },
        'city': {
            'description': 'Name of a city. The resultset contains institutions located in the selected city.',
            'type': 'string'
        },
        'deqar_id': {
            'description': 'DEQAR ID of an institution. The resultset contains institutions including the ',
                           'submitted string in their DEQAR ID.'
            'type': 'string'
        },
        'eter_id': {
            'description': 'ETER ID of an institution. The resultset contains institutions including the ',
                           'submitted string in their ETER.'
            'type': 'string'
        },
    }

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(InstitutionSearchInspector, self).get_filter_parameters(filter_backend)
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

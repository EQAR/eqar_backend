from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from rest_framework.filters import OrderingFilter


class CountryListInspector(CoreAPICompatInspector):
    fields = {
        'external_qaa': {
            'description': 'Filters the list if country is part of the external qaa. '
                           'Parameter values: 1 (no), 2 (partially / with conditions), 3 (yes)',
            'type': 'integer',
            'enum': [1, 2, 3]
        },
        'european_approach': {
            'description': 'Filters the list if European Approach is used in the country. '
                           'Parameter values: 1 (no), 2 (partially / with conditions), 3 (yes)',
            'type': 'integer',
            'enum': [1, 2, 3]
        },
        'eqar_governmental_member': {
            'description': 'Filters the list if the country is an EQAR governmental member.',
            'type': 'boolean'
        }
    }

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(CountryListInspector, self).get_filter_parameters(filter_backend)
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
            results = super(CountryListInspector, self).get_filter_parameters(filter_backend)

            if results != NotHandled:
                for param in results:
                    if param.get('name') == 'ordering':
                        param.enum = ['name_english', '-name_english', 'agency_count', '-agency_count']

            return results

        return NotHandled

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.inspectors import CoreAPICompatInspector, NotHandled
from rest_framework.filters import OrderingFilter


class AgencyListInspector(CoreAPICompatInspector):
    fields = {
        'registered': {
            'description': 'Filter agencies based on their registration status.',
            'type': 'string',
            'enum': ['True', 'False', 'All']
        }
    }
    ordering = ['name_primary', '-name_primary', 'acronym_primary', '-acronym_primary']

    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            results = super(AgencyListInspector, self).get_filter_parameters(filter_backend)
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
            results = super(AgencyListInspector, self).get_filter_parameters(filter_backend)

            if results != NotHandled:
                for param in results:
                    if self.ordering:
                        if param.get('name') == 'ordering':
                            param.enum = self.ordering

            return results

        return NotHandled

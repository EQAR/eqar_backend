from django.apps import AppConfig


class InstitutionsConfig(AppConfig):
    name = 'institutions'

    def ready(self):
        super(InstitutionsConfig, self).ready()
        from institutions.signals import set_institution_properties

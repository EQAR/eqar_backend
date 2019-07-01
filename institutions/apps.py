from django.apps import AppConfig


class InstitutionsConfig(AppConfig):
    name = 'institutions'

    def ready(self):
        super(InstitutionsConfig, self).ready()
        from institutions.signals import do_index_institutions_upon_institution_save
        from institutions.signals import do_index_institutions_upon_hierarchical_relationship_save
        from institutions.signals import do_index_institutions_upon_historical_relationship_save
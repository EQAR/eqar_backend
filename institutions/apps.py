from django.apps import AppConfig


class InstitutionsConfig(AppConfig):
    name = 'institutions'

    def ready(self):
        super(InstitutionsConfig, self).ready()
        from institutions.signals import do_index_institutions_upon_institution_save
        from institutions.signals import do_index_institutions_upon_institution_name_save
        from institutions.signals import do_index_institutions_upon_institution_name_version_save
        from institutions.signals import do_index_institutions_upon_institution_identifier_save
        from institutions.signals import do_index_institutions_upon_institution_country_save
        from institutions.signals import do_index_institutions_upon_institution_eter_save
        from institutions.signals import do_index_institutions_upon_hierarchical_relationship_save
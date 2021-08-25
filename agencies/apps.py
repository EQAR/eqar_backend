from django.apps import AppConfig


class AgenciesConfig(AppConfig):
    name = 'agencies'
    from agencies.signals import do_index_institutions_upon_agency_save
    from agencies.signals import do_index_agencies
    from agencies.signals import do_index_reports_upon_activity_name_change
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = 'reports'

    def ready(self):
        super(ReportsConfig, self).ready()
        from reports.signals import set_institution_has_reports
        from reports.signals import do_index_report
        from reports.signals import do_delete_report
        from reports.signals import do_reharvest_file_when_location_change
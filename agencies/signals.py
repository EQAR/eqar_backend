from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from agencies.models import Agency, AgencyName, AgencyNameVersion, AgencyFocusCountry, AgencyESGActivity
from institutions.tasks import index_institution


@receiver([post_save, post_delete], sender=Agency)
def do_index_institutions_upon_agency_save(sender, instance, **kwargs):
    for institution in instance.reports.institutions:
        index_institution.delay(institution.id)
        
        
@receiver([post_save, post_delete], sender=AgencyName)
def do_index_institutions_upon_agency_name_save(sender, instance, **kwargs):
    for institution in instance.agency.reports.institutions:
        index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=AgencyNameVersion)
def do_index_institutions_upon_agency_name_version_save(sender, instance, **kwargs):
    for institution in instance.agency_name.agency.reports.institutions:
        index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=AgencyFocusCountry)
def do_index_institutions_upon_agency_focus_country_save(sender, instance, **kwargs):
    for institution in instance.agency.reports.institutions:
        index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=AgencyESGActivity)
def do_index_institutions_upon_agency_esg_activity_save(sender, instance, **kwargs):
    for institution in instance.agency.reports.institutions:
        index_institution.delay(institution.id)


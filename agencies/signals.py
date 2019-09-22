from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from agencies.models import Agency
from agencies.tasks import index_agency
from institutions.tasks import index_institution


@receiver([post_save, post_delete], sender=Agency)
def do_index_institutions_upon_agency_save(sender, instance, **kwargs):
    for report in instance.report_set.iterator():
        for institution in report.institutions.iterator():
            index_institution.delay(institution.id)


@receiver([post_save], sender=Agency)
def do_index_agencies(sender, instance, **kwargs):
    index_agency.delay(instance.id)
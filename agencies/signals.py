from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from agencies.models import Agency
from institutions.tasks import index_institution


@receiver([post_save, post_delete], sender=Agency)
def do_index_institutions_upon_agency_save(sender, instance, **kwargs):
    for institution in instance.reports.institutions:
        index_institution.delay(institution.id)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from institutions.models import InstitutionName, Institution, InstitutionIdentifier, InstitutionNameVersion, \
    InstitutionCountry, InstitutionQFEHEALevel, InstitutionETERRecord, InstitutionHierarchicalRelationship, \
    InstitutionHistoricalRelationship
from institutions.tasks import index_institution


@receiver([post_save, post_delete], sender=InstitutionETERRecord)
def do_index_institutions_upon_institution_eter_save(sender, instance, **kwargs):
    institution = instance.institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=InstitutionQFEHEALevel)
def do_index_institutions_upon_institution_qf_ehea_level_save(sender, instance, **kwargs):
    institution = instance.institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=InstitutionCountry)
def do_index_institutions_upon_institution_country_save(sender, instance, **kwargs):
    institution = instance.institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=InstitutionIdentifier)
def do_index_institutions_upon_institution_identifier_save(sender, instance, **kwargs):
    institution = instance.institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=InstitutionNameVersion)
def do_index_institutions_upon_institution_name_version_save(sender, instance, **kwargs):
    institution = instance.institution_name_institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=InstitutionName)
def do_index_institutions_upon_institution_name_save(sender, instance, **kwargs):
    institution = instance.institution
    index_institution.delay(institution.id)


@receiver([post_save, post_delete], sender=Institution)
def do_index_institutions_upon_institution_save(sender, instance, **kwargs):
    index_institution.delay(instance.id)


@receiver([post_save, post_delete], sender=InstitutionHierarchicalRelationship)
def do_index_institutions_upon_hierarchical_relationship_save(sender, instance, **kwargs):
    institution_parent = instance.institution_parent
    institution_child = instance.institution_child
    index_institution.delay(institution_parent.id)
    index_institution.delay(institution_child.id)


@receiver([post_save, post_delete], sender=InstitutionHistoricalRelationship)
def do_index_institutions_upon_historical_relationship_save(sender, instance, **kwargs):
    institution_source = instance.institution_source
    institution_target = instance.institution_target
    index_institution.delay(institution_source.id)
    index_institution.delay(institution_target.id)



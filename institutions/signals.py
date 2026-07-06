from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from institutions.models import Institution, InstitutionHierarchicalRelationship, InstitutionHistoricalRelationship
from institutions.tasks import index_institution, delete_institution, meili_index_institution, meili_delete_institution


@receiver([post_save], sender=Institution)
def do_index_institutions_upon_institution_save(sender, instance, **kwargs):
    if not instance.deqar_id:
        instance.create_deqar_id()
    transaction.on_commit(lambda: index_institution.delay(instance.id))
    transaction.on_commit(lambda: meili_index_institution.delay(instance.id))

@receiver([pre_delete], sender=Institution)
def do_remove_institutions_upon_institution_delete(sender, instance, **kwargs):
    institution_id = instance.id
    transaction.on_commit(lambda: delete_institution.delay(institution_id))
    transaction.on_commit(lambda: meili_delete_institution.delay(institution_id))

@receiver([post_save, post_delete], sender=InstitutionHierarchicalRelationship)
def do_index_institutions_upon_hierarchical_relationship_save(sender, instance, **kwargs):
    institution_parent = instance.institution_parent
    institution_child = instance.institution_child
    # a (non-platform) parent inherits its child's reports, so its has_report may change
    institution_parent.update_has_report()
    institution_child.update_has_report()
    transaction.on_commit(lambda: index_institution.delay(institution_parent.id))
    transaction.on_commit(lambda: meili_index_institution.delay(institution_parent.id))
    transaction.on_commit(lambda: index_institution.delay(institution_child.id))
    transaction.on_commit(lambda: meili_index_institution.delay(institution_child.id))


@receiver([post_save, post_delete], sender=InstitutionHistoricalRelationship)
def do_index_institutions_upon_historical_relationship_save(sender, instance, **kwargs):
    institution_source = instance.institution_source
    institution_target = instance.institution_target
    # succeeded/absorbed relationships let one side inherit the other's reports; recompute both
    institution_source.update_has_report()
    institution_target.update_has_report()
    transaction.on_commit(lambda: index_institution.delay(institution_source.id))
    transaction.on_commit(lambda: meili_index_institution.delay(institution_source.id))
    transaction.on_commit(lambda: index_institution.delay(institution_target.id))
    transaction.on_commit(lambda: meili_index_institution.delay(institution_target.id))

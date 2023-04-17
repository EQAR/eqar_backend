from celery.task import task

from institutions.indexers.institution_indexer import InstitutionIndexer


@task(name="index_institution")
def index_institution(institution_id):
    indexer = InstitutionIndexer(institution_id)
    indexer.index()


@task(name="delete_institution")
def delete_institution(institution_id):
    indexer = InstitutionIndexer(institution_id)
    indexer.delete()

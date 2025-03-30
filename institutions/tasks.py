from celery.task import task

from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.indexers.institution_meili_indexer import InstitutionIndexer as MeiliInstitutionIndexer


@task(name="index_institution")
def index_institution(institution_id):
    indexer = InstitutionIndexer(institution_id)
    indexer.index()

@task(name="meili_index_institution")
def meili_index_institution(institution_id):
    # index institution
    indexer = MeiliInstitutionIndexer()
    indexer.index(institution_id)

@task(name="delete_institution")
def delete_institution(institution_id):
    indexer = InstitutionIndexer(institution_id)
    indexer.delete()

@task(name="meili_delete_institution")
def meili_delete_institution(institution_id):
    # delete institution
    indexer = MeiliInstitutionIndexer()
    indexer.delete(institution_id)

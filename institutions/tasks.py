from celery.task import task

from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution


@task(name="index_institution")
def index_institution(institution_id):
    institution = Institution.objects.get(id=institution_id)
    indexer = InstitutionIndexer(institution)
    indexer.index()

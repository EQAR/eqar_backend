from celery.task import task

from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency


@task(name="index_agency")
def index_agency(agency_id):
    agency = Agency.objects.get(id=agency_id)
    indexer = AgencyIndexer(agency)
    indexer.index()

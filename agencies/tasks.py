from celery.task import task

from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency
from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution


@task(name="index_agency")
def index_agency(agency_id):
    agency = Agency.objects.get(id=agency_id)
    indexer = AgencyIndexer(agency)
    indexer.index()


@task(name="index_institutions_when_agency_saved")
def index_institutions_when_agency_saved(agency_id):
    institutions = Institution.objects.filter(reports__agency__id=agency_id).distinct()
    print(institutions.count())
    for inst in institutions.all():
        indexer = InstitutionIndexer(inst)
        indexer.index()

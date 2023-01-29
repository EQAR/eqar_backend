from celery.task import task
from django.db.models import Q

from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency
from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution
from reports.indexers.reports_indexer import ReportsIndexer
from reports.models import Report


@task(name="index_agency")
def index_agency(agency_id):
    agency = Agency.objects.get(id=agency_id)
    indexer = AgencyIndexer(agency)
    indexer.index()


@task(name="index_reports_when_agency_acronym_changes")
def index_reports_when_agency_acronym_changes(agency_id):
    reports = Report.objects.filter(Q(agency__id=agency_id) | Q(contributing_agencies__id=agency_id)).distinct()
    for report in reports.all():
        indexer = ReportsIndexer(report)
        indexer.index()


@task(name="index_institutions_when_agency_acronym_changes")
def index_institutions_when_agency_acronym_changes(agency_id):
    institutions = Institution.objects.filter(reports__agency__id=agency_id).distinct()
    for inst in institutions.all():
        indexer = InstitutionIndexer(inst)
        indexer.index()

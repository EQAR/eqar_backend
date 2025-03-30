from celery.task import task

from reports.indexers.reports_indexer import ReportsIndexer
from reports.indexers.report_meili_indexer import ReportIndexer as MeiliReportIndexer
from programmes.indexers.programme_indexer import ProgrammeIndexer
from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.indexers.institution_meili_indexer import InstitutionIndexer as MeiliInstitutionIndexer
from reports.models import Report


@task(name="index_report")
def index_report(report_id):
    indexer = ReportsIndexer(report_id)
    indexer.index()

@task(name="meili_index_report")
def meili_index_report(report_id):
    report = Report.objects.get(pk=report_id)
    # index report
    indexer = MeiliReportIndexer()
    indexer.index(report.id)
    # index programmes
    indexer = ProgrammeIndexer()
    for programme in report.programme_set.iterator():
        indexer.index(programme.id)
    # index institutions
    meili_indexer = MeiliInstitutionIndexer()
    for institution in report.institutions.iterator():
        indexer = InstitutionIndexer(institution.id)
        indexer.index()
        meili_indexer.index(institution.id)

@task(name="index_delete_report")
def index_delete_report(report_id):
    indexer = ReportsIndexer(report_id)
    indexer.delete()

@task(name="meili_delete_report")
def meili_delete_report(report_id, programme_ids, institution_ids):
    # delete programmes
    indexer = ProgrammeIndexer()
    for programme_id in programme_ids:
        indexer.delete(programme_id)
    # delete report
    indexer = MeiliReportIndexer()
    indexer.delete(report_id)
    # re-index institutions
    meili_indexer = MeiliInstitutionIndexer()
    for institution_id in institution_ids:
        indexer = InstitutionIndexer(institution_id)
        indexer.index()
        meili_indexer.index(institution_id)


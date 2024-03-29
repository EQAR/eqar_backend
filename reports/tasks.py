from celery.task import task

from reports.indexers.reports_indexer import ReportsIndexer
from reports.models import Report


@task(name="index_report")
def index_report(report_id):
    indexer = ReportsIndexer(report_id)
    indexer.index()


@task(name="index_delete_report")
def index_delete_report(report_id):
    indexer = ReportsIndexer(report_id)
    indexer.delete()

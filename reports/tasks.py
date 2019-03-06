from celery.task import task

from reports.indexers.reports_all_indexer import ReportsAllIndexer
from reports.models import Report


@task(name="index_report")
def index_report(report_id):
    report = Report.objects.get(id=report_id)
    indexer = ReportsAllIndexer(report)
    indexer.index()

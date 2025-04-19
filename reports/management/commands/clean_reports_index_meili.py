from django.conf import settings

from eqar_backend.meilisearch import CheckMeiliIndex

from reports.indexers.report_meili_indexer import ReportIndexer

class Command(CheckMeiliIndex):
    help = 'Delete reports from Meilisearch index that no longer exist and add missing ones'
    PAGESIZE = 5000
    indexer = ReportIndexer

    def _to_string(self, r):
        return f"Agency {r.agency['acronym_primary']}, Activity ID {'/'.join([ str(i['id']) for i in r.agency_esg_activities])} @ {', '.join([ i['name_sort'] for i in r.institutions ])}"


from django.conf import settings

from eqar_backend.meilisearch import CheckMeiliIndex

from programmes.indexers.programme_indexer import ProgrammeIndexer

class Command(CheckMeiliIndex):
    help = 'Delete programmes from Meilisearch index that no longer exist and add missing ones'
    PAGESIZE = 5000
    indexer = ProgrammeIndexer

    def _to_string(self, r):
        return f"{r.name_primary} ({r.qf_ehea_level}) @ {', '.join(['DEQARINST%04d' % i for i in r.institutions])}"


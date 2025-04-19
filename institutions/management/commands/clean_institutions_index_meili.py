from django.conf import settings

from eqar_backend.meilisearch import CheckMeiliIndex

from institutions.indexers.institution_meili_indexer import InstitutionIndexer

class Command(CheckMeiliIndex):
    help = 'Delete institutions from Meilisearch index that no longer exist and add missing ones'
    PAGESIZE = 2500
    indexer = InstitutionIndexer

    def _to_string(self, r):
        return f"{r.deqar_id} {r.name_primary} ({r.eter_id})"


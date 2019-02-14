import pysolr
from django.conf import settings

from eqar_backend import searchers


class InstitutionAllSearcher(searchers.Searcher):
    """
    Class to search all Institution records from Solr.
    """

    def get_tie_breaker(self, ordering):
        # Tie breaker
        if ordering == 'score':
            return 'name_sort asc,id asc'
        else:
            return 'score desc,id asc'

import pysolr
from django.conf import settings


class Searcher:
    """
    Class to search records from Solr.
    """

    def __init__(self, solr_core):
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.q = {}
        self.fq = []
        self.sort = ""
        self.qf = ""
        self.fl = ""
        self.start = 0
        self.rows_per_page = 10
        self.tie_breaker = ""
        self.paginated = True

    def initialize(self, params, start=0, rows_per_page=10, tie_breaker="", paginated=True):
        self.start = start
        self.rows_per_page = rows_per_page
        self.tie_breaker = tie_breaker
        self.paginated = paginated

        search = params.get('search', '')
        self.set_q(search)

        filters = params.get('filters', [])
        self.set_fq(filters)

        date_filters = params.get('date_filters', [])
        self.set_date_fq(date_filters)

        ordering = params.get('ordering', "")
        self.set_order(ordering)

        qf = params.get('qf', '')
        self.set_qf(qf)

        fl = params.get('fl', '')
        self.set_fl(fl)

    def search(self, cursor_mark=''):
        search_kwargs = {
            'defType': 'edismax',
            'qf': self.qf,
            'fq': self.fq,
            'fl': self.fl,
            'q.op': 'AND'
        }
        if self.paginated:
            return self.solr.search(
                q=self.q,
                sort=self.sort,
                start=self.start,
                rows=self.rows_per_page,
                **search_kwargs
            )
        else:
            return self.solr.search(
                q=self.q,
                sort=self.sort,
                cursorMark=cursor_mark,
                **search_kwargs
            )

    def set_q(self, search):
        self.q = search
        if search == "":
            self.q = "*:*"

    def set_fq(self, filters):
        for f in filters:
            for k, v in f.items():
                self.fq.append('%s:"%s"' % (k, v))

    def set_date_fq(self, date_filters):
        for f in date_filters:
            for k, v in f.items():
                self.fq.append('%s:%s' % (k, v))

    def get_tie_breaker(self, ordering):
        # Tie breaker
        if ordering == 'score':
            if len(self.tie_breaker) > 0:
                return '%s,id asc' % self.tie_breaker
            else:
                return 'id asc'
        else:
            return 'score desc,id asc'

    def set_order(self, ordering):
        # Ordering params
        ordering_direction = 'asc'
        if ordering == '':
            ordering = '-score'

        if ordering[0] == '-':
            ordering = ordering[1:]
            ordering_direction = 'desc'

        tie_breaker = self.get_tie_breaker(ordering)
        self.sort = "%s %s,%s" % (ordering, ordering_direction, tie_breaker)

    def set_qf(self, qf):
        self.qf = " ".join(qf)

    def set_fl(self, fl):
        self.fl = fl

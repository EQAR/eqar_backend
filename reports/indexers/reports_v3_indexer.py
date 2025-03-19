import json

import pysolr
from django.conf import settings

from reports.models import Report
from reports.serializers.v3.report_indexer_serializer import ReportIndexerSerializer


class ReportsIndexerV3:
    """
    Class to index Reports to Solr.
    """

    def __init__(self, report_id):
        self.report_id = report_id
        self.report = self._get_report(report_id)
        self.solr_core = getattr(settings, "SOLR_CORE_REPORTS_V3", "deqar-reports-v3")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url, always_commit=True)
        self.doc = {}

    def create_solr_document(self):
        self._index_report()
        self._store_json()
        self._remove_duplicates()

    def get_solr_document(self):
        return self.doc

    def index(self):
        self.create_solr_document()
        try:
            self.solr.add([self.doc])
            print("Indexing Report No. %s!" % (self.doc['id']))
        except pysolr.SolrError as e:
            print('Error with Report No. %s! Error: %s' % (self.doc['id'], e))

    def delete(self):
        self.solr.delete(id=self.report_id, commit=True)

    def _get_report(self, report_id):
        qs = Report.objects.filter(pk=report_id)
        qs = qs.select_related('agency')
        qs = qs.select_related('agency_esg_activity')
        qs = qs.select_related('status')
        qs = qs.select_related('decision')
        qs = qs.select_related('flag')
        qs = qs.prefetch_related('agency__agencyfocuscountry_set')
        qs = qs.prefetch_related('contributing_agencies')
        qs = qs.prefetch_related('institutions',
                                 'institutions__institutioncountry_set',
                                 'institutions__relationship_parent', 'institutions__relationship_child',
                                 'institutions__relationship_source', 'institutions__relationship_target')
        qs = qs.prefetch_related('programme_set', 'programme_set__countries', 'programme_set__programmename_set')
        qs = qs.prefetch_related('reportfile_set', 'reportfile_set__languages')
        return qs.get()

    def _index_report(self):
        serializer = ReportIndexerSerializer(self.report)
        self.doc = serializer.data

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _store_json(self):
        self.doc['institutions'] = json.dumps(self.doc['institutions'])
        self.doc['programmes'] = json.dumps(self.doc['programmes'])
        self.doc['country'] = json.dumps(self.doc['country'])

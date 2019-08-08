from datetime import datetime, date

import pysolr
from django.conf import settings


class ReportsAllIndexer:
    """
    Class to index Reports to Solr.
    """

    def __init__(self, report):
        self.report = report
        self.solr_core = getattr(settings, "SOLR_CORE_REPORTS_ALL", "deqar-reports-all")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.doc = {
            'id': None,
            'agency': None,
            'local_id': [],
            'country': [],
            'city': [],
            'activity': None,
            'institution_name_primary': None,
            'institution_name_english': [],
            'institution_name_official': [],
            'institution_name_official_transliterated': [],
            'institution_name_version': [],
            'institution_name_version_transliterated': [],
            'programme_name_primary': None,
            'programme_name': [],
            'flag_level': None,
            'valid_from': None,
            'valid_to': None,
            'user_created': None,
            'date_created': None,
            'date_updated': None
        }

    def index(self):
        self._index_report()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
        except pysolr.SolrError as e:
            print('Error with Report No. %s! Error: %s' % (self.doc['id'], e))

    def _index_report(self):
        self.doc['id'] = self.report.id
        self.doc['local_id'] = self.report.local_identifier
        self.doc['agency'] = self.report.agency.acronym_primary
        self.doc['activity'] = self.report.agency_esg_activity.activity
        self.doc['activity_type'] = self.report.agency_esg_activity.activity_type.type
        self.doc['flag_level'] = self.report.flag.flag

        self.doc['user_created'] = self.report.created_by.username
        self.doc['date_created'] = "%sZ" % self.report.created_at.isoformat()
        self.doc['date_updated'] = "%sZ" % self.report.updated_at.isoformat()

        self.doc['valid_from'] = "%sZ" % datetime.combine(self.report.valid_from, datetime.min.time()).isoformat()
        if self.report.valid_to:
            valid_to = "%sZ" % datetime.combine(self.report.valid_to, datetime.min.time()).isoformat()
            self.doc['valid_to'] = valid_to
            self.doc['valid_to_calculated'] = valid_to
        else:
            valid_to = self._add_years(self.report.valid_from, 5)
            valid_to = "%sZ" % datetime.combine(valid_to, datetime.min.time()).isoformat()
            self.doc['valid_to_calculated'] = valid_to

        # Institutions indexing
        institutions = []
        for inst in self.report.institutions.iterator():

            institutions.append(inst.name_primary)
            for iname in inst.institutionname_set.all():
                self.doc['institution_name_official'].append(iname.name_official.strip())
                self.doc['institution_name_official_transliterated'].append(iname.name_official_transliterated.strip())
                self.doc['institution_name_english'].append(iname.name_english.strip())

                for iname_version in iname.institutionnameversion_set.all():
                    self.doc['institution_name_version'].append(iname_version.name.strip())
                    self.doc['institution_name_version_transliterated'].append(iname_version.transliteration.strip())

            for c in inst.institutioncountry_set.all():
                self.doc['country'].append(c.country.name_english)
                self.doc['city'].append(c.city)

        self.doc['institution_name_official'] = list(
            filter(None, self.doc['institution_name_official']))
        self.doc['institution_name_official_transliterated'] = list(
            filter(None, self.doc['institution_name_official_transliterated']))
        self.doc['institution_name_english'] = list(
            filter(None, self.doc['institution_name_english']))
        self.doc['institution_name_version'] = list(
            filter(None, self.doc['institution_name_version']))
        self.doc['institution_name_version_transliterated'] = list(
            filter(None, self.doc['institution_name_version_transliterated']))

        # Programmes indexing
        programmes = []
        for programme in self.report.programme_set.all():
            programmes.append(programme.name_primary)

            for pname in programme.programmename_set.all():
                self.doc['programme_name'].append(pname.name.strip())

            for c in programme.countries.all():
                self.doc['country'].append(c.name_english)

        institutions = "; ".join(institutions)
        programmes = " / ".join(programmes)

        if len(programmes) > 0:
            ipdisplay = "%s - %s" % (institutions, programmes)
        else:
            ipdisplay = institutions

        self.doc['institution_programme_primary'] = ipdisplay
        self.doc['institution_programme_sort'] = ipdisplay

        self.doc['programme_name'] = list(filter(None, self.doc['programme_name']))

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _remove_empty_keys(self):
        new_doc = {k: v for k, v in self.doc.items() if v}
        self.doc.clear()
        self.doc.update(new_doc)

    @staticmethod
    def _add_years(d, years):
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

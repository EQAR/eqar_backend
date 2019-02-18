import pysolr
from django.conf import settings

from reports.models import Report


class InstitutionAllIndexer:
    """
    Class to index Institution records to Solr.
    """

    def __init__(self, institution):
        self.institution = institution
        self.solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS_ALL", "deqar-institutions-all")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.doc = {
            'id': None,
            'eter_id': None,
            'national_identifier': None,
            'name_primary': None,
            'name_select_display': None,
            'name_sort': None,
            'name_official': [],
            'name_official_transliterated': [],
            'name_english': [],
            'name_version': [],
            'name_version_transliterated': [],
            'place': [],
            'country': [],
            'city': []
        }

    def index(self):
        self._index_institution()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
            print('Indexed Institution No. %s!' % self.doc['id'])
        except pysolr.SolrError as e:
            print('Error with Institution No. %s! Error: %s' % (self.doc['id'], e))

    def _index_institution(self):
        self.doc['id'] = self.institution.id
        self.doc['national_identifier'] = self.institution.national_identifier
        self.doc['name_primary'] = self.institution.name_primary.strip()
        self.doc['name_sort'] = self.institution.name_sort.strip()
        self.doc['website_link'] = self.institution.website_link.strip()

        select_display = self.institution.name_primary.strip()
        if self.institution.eter:
            self.doc['eter_id'] = self.institution.eter.eter_id
            select_display += ' (%s)' % self.institution.eter.eter_id
        self.doc['name_select_display'] = select_display

        # Index name versions
        for iname in self.institution.institutionname_set.all():
            self.doc['name_official'].append(iname.name_official.strip())
            self.doc['name_official_transliterated'].append(iname.name_official_transliterated.strip())
            self.doc['name_english'].append(iname.name_english.strip())

            for iname_version in iname.institutionnameversion_set.all():
                self.doc['name_version'].append(iname_version.name.strip())
                self.doc['name_version_transliterated'].append(iname_version.transliteration.strip())

        self.doc['name_official'] = list(filter(None, self.doc['name_official']))
        self.doc['name_official_transliterated'] = list(filter(None, self.doc['name_official_transliterated']))
        self.doc['name_english'] = list(filter(None, self.doc['name_english']))
        self.doc['name_version'] = list(filter(None, self.doc['name_version']))
        self.doc['name_version_transliterated'] = list(filter(None, self.doc['name_version_transliterated']))

        # Index places
        for icountry in self.institution.institutioncountry_set.iterator():
            self.doc['country'].append(icountry.country.name_english.strip())
            if icountry.city:
                self.doc['city'].append(icountry.city.strip())
                self.doc['place'].append("%s (%s)" % (icountry.city.strip(),
                                                      icountry.country.name_english.strip()))
            else:
                self.doc['place'].append(icountry.country.name_english.strip())

        self.doc['place'] = list(filter(None, self.doc['place']))
        self.doc['country'] = list(filter(None, self.doc['country']))
        self.doc['city'] = list(filter(None, self.doc['city']))

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _remove_empty_keys(self):
        new_doc = {k: v for k, v in self.doc.items() if v}
        self.doc.clear()
        self.doc.update(new_doc)


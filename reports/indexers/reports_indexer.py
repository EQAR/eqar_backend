import json
from datetime import datetime, date

import pysolr
from datedelta import datedelta
from django.conf import settings
from django.db.models import Q


class ReportsIndexer:
    """
    Class to index Reports to Solr.
    """

    def __init__(self, report):
        self.report = report
        self.solr_core = getattr(settings, "SOLR_CORE_REPORTS", "deqar-reports")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.doc = {
            'id': None,
            'local_id': None,
            'agency_name': None,
            'agency_acronym': None,
            'agency_url': None,
            'agency_esg_activity': None,
            'agency_esg_activity_type': None,
            'name': None,
            'institutions': [],
            'institutions_hierarchical': [],
            'institutions_historical': [],
            'programmes': [],
            'report_valid': False,
            'valid_from': None,
            'valid_to': None,
            'status': None,
            'decision': None,
            'report_files': [],
            'report_links': [],
            'other_comment': None,
            'user_created': None,
            'date_created': None,
            'date_updated': None,
            'flag_level': None,

            'id_search': None,
            'country': [],
            'city': [],
            'activity': None,
            'institution_programme_primary': None,
            'institution_name_english': [],
            'institution_name_official': [],
            'institution_name_official_transliterated': [],
            'institution_name_version': [],
            'institution_name_version_transliterated': [],
            'programme_name': [],
            'valid_to_calculated': None,

            'agency_id': 0,
            'country_id': [],
            'activity_id': 0,
            'activity_type_id': 0,
            'status_id': 0,
            'decision_id': 0,
            'language_id': [],

            'id_sort': 0,
            'agency_sort': None,
            'institution_programme_sort': None,

            'agency_facet': None,
            'country_facet': [],
            'activity_facet': None,
            'activity_type_facet': None,
            'status_facet': None,
            'decision_facet': None,
            'language_facet': [],
            'flag_level_facet': None,
            'crossborder_facet': []
        }

    def index(self):
        self._index_report()
        self._store_json()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
            print("Indexing Report No. %s!" % (self.doc['id']))
        except pysolr.SolrError as e:
            print('Error with Report No. %s! Error: %s' % (self.doc['id'], e))

    def _index_report(self):
        self.doc['id'] = self.report.id
        self.doc['id_sort'] = self.report.id
        self.doc['id_search'] = self.report.id
        self.doc['local_id'] = self.report.local_identifier
        self.doc['name'] = self.report.agency_esg_activity.activity_description

        self.doc['agency_esg_activity'] = self.report.agency_esg_activity.activity
        self.doc['activity_facet'] = self.report.agency_esg_activity.activity
        self.doc['activity_id'] = self.report.agency_esg_activity.id

        self.doc['agency_esg_activity_type'] = self.report.agency_esg_activity.activity_type.type
        self.doc['activity_type_facet'] = self.report.agency_esg_activity.activity_type.type
        self.doc['activity_type_id'] = self.report.agency_esg_activity.activity_type.id

        self.doc['agency_name'] = self.report.agency.name_primary
        self.doc['agency_acronym'] = self.report.agency.acronym_primary
        self.doc['agency_sort'] = self.report.agency.acronym_primary
        self.doc['agency_url'] = self.report.agency.website_link
        self.doc['agency_facet'] = self.report.agency.acronym_primary
        self.doc['agency_id'] = self.report.agency.id

        self.doc['report_valid'] = self._set_report_valid()

        self.doc['status'] = self.report.status.status
        self.doc['status_facet'] = self.report.status.status
        self.doc['status_id'] = self.report.status.id

        self.doc['decision'] = self.report.decision.decision
        self.doc['decision_facet'] = self.report.decision.decision
        self.doc['decision_id'] = self.report.decision.id

        # Index Report Files
        for report_file in self.report.reportfile_set.iterator():
            self.doc['report_files'].append({
                'file_display_name': report_file.file_display_name,
                'file': report_file.file.url if report_file.file else None,
                'languages': [lang.language_name_en for lang in report_file.languages.all()]
            })
            for lang in report_file.languages.all():
                self.doc['language_facet'].append(lang.language_name_en)
                self.doc['language_id'].append(lang.id)

        # Index Report Links
        for report_link in self.report.reportlink_set.iterator():
            self.doc['report_links'].append({
                'link_display_name': report_link.link_display_name,
                'link': report_link.link
            })

        # Crossborder filter
        self.doc['crossborder_facet'].append(False)
        focus_countries = self.report.agency.agencyfocuscountry_set
        for inst in self.report.institutions.iterator():
            for ic in inst.institutioncountry_set.iterator():
                if focus_countries.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=True)):
                    self.doc['crossborder_facet'].append(True)

        self.doc['other_comment'] = self.report.other_comment

        self.doc['flag_level'] = self.report.flag.flag
        self.doc['flag_level_facet'] = self.report.flag.flag

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
            self.doc['institutions'].append({
                'id': inst.id,
                'deqar_id': inst.deqar_id,
                'name_primary': inst.name_primary,
                'website_link': inst.website_link
            })

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
                self.doc['country_facet'].append(c.country.name_english)
                self.doc['country_id'].append(c.country.id)
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
        for programme in self.report.programme_set.iterator():
            self.doc['programmes'].append({
                'id': programme.id,
                'name_primary': programme.name_primary,
                'nqf_level': programme.nqf_level,
                'qf_ehea_level': programme.qf_ehea_level.level if programme.qf_ehea_level else None
            })

            programmes.append(programme.name_primary)

            for pname in programme.programmename_set.iterator():
                self.doc['programme_name'].append(pname.name.strip())

            for c in programme.countries.iterator():
                self.doc['country'].append(c.name_english)
                self.doc['country_facet'].append(c.name_english)
                self.doc['country_id'].append(c.id)

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

    def _store_json(self):
        self.doc['institutions'] = json.dumps(self.doc['institutions'])
        self.doc['programmes'] = json.dumps(self.doc['programmes'])
        self.doc['report_files'] = json.dumps(self.doc['report_files'])
        self.doc['report_links'] = json.dumps(self.doc['report_links'])

    def _set_report_valid(self):
        valid_from = self.report.valid_from
        valid_to = self.report.valid_to
        valid = True

        # Check if valid_from less than equal then todays date - 6 years and valid_to isn't set
        if valid_from <= date.today()-datedelta(years=6) and valid_to is None:
            valid = False

        # Check if valid_to lest than equal then todays date
        if valid_to:
            if valid_to <= date.today():
                valid = False

        return valid

    @staticmethod
    def _add_years(d, years):
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))



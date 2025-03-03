from submissionapi.populators.programme_populator import ProgrammePopulator
from submissionapi.populators.report_populator import ReportPopulator


class Populator():
    """
    Class to handle the population of data from the submission endpoints.
    """
    def __init__(self, data, user):
        self.data = data
        self.user = user
        self.submission_status = "success"
        self.sanity_check_status = "success"
        self.institution_flag_log = []
        self.report = None
        self.agency = None

    def populate(self):
        # Save submitted agency record
        self.agency = self.data.get('agency', None)

        # Report record populate
        self._report_upsert()

        # Institution record populate
        self._institution_upsert()

        # Platform record populate
        self._platform_upsert()

        # Programme record populate
        self._programme_insert()

    def _report_upsert(self):
        """
        Create or insert Report instance.
        """
        rp = ReportPopulator(self.data, self.agency, self.user)
        rp.populate()
        self.report = rp.report

    def _institution_upsert(self):
        """
        Create or insert Institution instance.
        """
        self.report.institutions.clear()
        institutions = self.data.get('institutions', None)

        for institution in institutions:
            self.report.institutions.add(institution)

    def _platform_upsert(self):
        """
        Create or insert Platform instance.
        """
        self.report.platforms.clear()
        platforms = self.data.get('platforms', None)

        for platform in platforms:
            self.report.platforms.add(platform)

    def _programme_insert(self):
        """
        Create Programme instance.
        """
        # Remove all existing programme data
        self.report.programme_set.all().delete()
        programmes = self.data.get('programmes', [])
        for programme in programmes:
            pp = ProgrammePopulator(programme, self.agency, self.report)
            pp.populate()
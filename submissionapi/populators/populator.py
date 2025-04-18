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

    def populate(self, action='upsert'):
        # Save submitted agency record
        self.agency = self.data.get('agency', None)

        # Report record populate
        if action == 'create':
            self._report_create()

        if action == 'update':
            self._report_update()

        if action == 'upsert':
            self._report_upsert()

        # Institution record populate
        self._institution_upsert()

        # Platform record populate
        self._platform_upsert()

        # Programme record populate
        self._programme_insert()

    def _report_create(self):
        """
        Create Report instance.
        """
        rp = ReportPopulator(self.data, self.agency, self.user)
        rp.create()
        self.report = rp.report

    def _report_update(self):
        """
        Update Report instance.
        """
        rp = ReportPopulator(self.data, self.agency, self.user)
        rp.update()
        self.report = rp.report

    def _report_upsert(self):
        """
        Create or update Report instance.
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
        platforms = self.data.get('platforms', None)

        if platforms:
            self.report.platforms.clear()
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

# wrapper for Python meilisearch module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand

import sys

import meilisearch

TESTING = sys.argv[1:2] == [ 'test' ]

class MeiliError(Exception):
    """
    Generic error when talking to Meilisearch API
    """

class MeiliTaskFailed(MeiliError):
    """
    Raised when asynchronous task finished as failed
    """

class MeiliTaskCanceled(MeiliError):
    """
    Raised when asynchronous task was cancelled
    """

class MeiliClient:
    """
    wrapper for the meilisearch.Client class
    """
    def __init__(self):
        if not hasattr(settings, "MEILI_API_URL"):
            raise MeiliError(f'Missing MEILI_API_URL setting')
        key = getattr(settings, "MEILI_API_KEY", None)
        self.meili = meilisearch.Client(settings.MEILI_API_URL, key)
        self.timeout = getattr(settings, "MEILI_WAIT_TIMEOUT", 6000 if TESTING else 1200000)
        self.interval = getattr(settings, "MEILI_WAIT_INTERVAL", 250 if TESTING else 1000)

    def _get_index_uid(self, setting, default):
        """
        prepend index name by test_ if we are running a test
        """
        index = getattr(settings, setting, default)
        if TESTING:
            return 'test_' + index
        else:
            return index

    @property
    def INDEX_PROGRAMMES(self):
        return self._get_index_uid("MEILI_INDEX_PROGRAMMES", 'programmes-v3')

    @property
    def INDEX_REPORTS(self):
        return self._get_index_uid("MEILI_INDEX_REPORTS", 'reports-v3')

    @property
    def INDEX_INSTITUTIONS(self):
        return self._get_index_uid("MEILI_INDEX_INSTITUTIONS", 'institutions-v3')

    def wait_for(self, task_info):
        """
        wrapper around wait_for_task with error handling
        """
        task = self.meili.wait_for_task(task_info.task_uid, timeout_in_ms=self.timeout, interval_in_ms=self.interval)

        if task.status == 'succeeded':
            return task
        elif task.status == 'failed':
            raise MeiliTaskFailed(task.error['message'])
        elif task.status == 'canceled':
            raise MeiliTaskCanceled(f'Task {task.uid} was cancelled by task {task.canceled_by}')
        else:
            raise MeiliError(f'Task {task.uid} finished with unknown status: {task.status}')

    def create_index(self, index, primary_key = 'id'):
        """
        Create a new index (if it does not exist) and in test mode flush all documents
        """
        try:
            self.meili.get_index(index)
            if TESTING:
                return self.wait_for(self.meili.index(index).delete_all_documents())
            else:
                return True
        except meilisearch.errors.MeilisearchApiError as e:
            if e.code == 'index_not_found':
                return self.wait_for(self.meili.create_index(index, { 'primaryKey': 'id' }))
            else:
                raise e

    def update_settings(self, index, settings):
        """
        Update the index settings
        """
        self.meili.get_index(index)
        return self.meili.index(index).update_settings(settings)

    def add_document(self, index, doc):
        """
        Add or update a document to the index
        """
        return self.meili.index(index).add_documents(doc)

    def delete_document(self, index, doc_id):
        """
        Delete a document from the index
        """
        return self.meili.index(index).delete_document(doc_id)


class MeiliIndexer:
    """
    generic indexer for Meilisearch
    """
    def __init__(self, sync=True):
        self.meili = MeiliClient()
        self.index_uid = getattr(self.meili, 'INDEX_' + self.model._meta.model_name.upper() + 'S')
        self.sync = sync

    def index(self, obj_id):
        obj = self.model.objects.get(pk=obj_id)
        doc = self.serializer(obj).data
        taskinfo = self.meili.add_document(self.index_uid, doc)
        if self.sync:
            return self.meili.wait_for(taskinfo)
        else:
            return taskinfo

    def delete(self, obj_id):
        taskinfo = self.meili.delete_document(self.index_uid, obj_id)
        if self.sync:
            return self.meili.wait_for(taskinfo)
        else:
            return taskinfo


class CheckMeiliIndex(BaseCommand):
    """
    generic management command to check whether deleted objects remain in Meilisearch index
    or whether objects are missing
    """
    PAGESIZE = 5000 # how many documents to fetch from Meili at once
    indexer = None
    model = None

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show records, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted objects")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for objects missing from the index")

    def _to_string(self, record):
        return f"[{self.model._meta.verbose_name} #{record.id}]"

    def handle(self, *args, **options):
        meili = MeiliClient()
        indexer = self.indexer(sync=False)
        if self.model is None:
            self.model = indexer.model

        offset = 0
        total = 1
        in_meili = set()
        to_delete = []
        while offset < total:
            self.stdout.write(f"\rChecking {self.model._meta.verbose_name} {offset}-{offset+self.PAGESIZE-1} of {total}", ending='')
            response = meili.meili.index(indexer.index_uid).get_documents({ 'offset': offset, 'limit': self.PAGESIZE })
            if response.total > total:
                total = response.total
            for r in response.results:
                in_meili.add(int(r.id))
                if not options['only_missing']:
                    try:
                        self.model.objects.get(id=r.id)
                    except self.model.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"\rdeleted {self.model._meta.verbose_name} {r.id} still in Meili index: {self._to_string(r)}"))
                        to_delete.append(r.id)
            offset += self.PAGESIZE
        self.stdout.write('')

        if not options['dry_run']:
            for i in to_delete:
                indexer.delete(i)
                self.stdout.write(self.style.ERROR(f"deleted {self.model._meta.verbose_name} {i} from Meili index"))

        self.stdout.write(f'\r{len(to_delete)} deleted {self.model._meta.verbose_name_plural} were still in Meilisearch')

        if not options['only_deleted']:
            missing_meili = 0
            for r in self.model.objects.iterator():
                if r.id in in_meili:
                    self.stdout.write(f"\r{self.model._meta.verbose_name} {r.id} is in Meilisearch", ending='')
                else:
                    self.stdout.write(self.style.WARNING(f"\r{self.model._meta.verbose_name} {r.id} is missing from Meilisearch"), ending='')
                    if not options['dry_run']:
                        indexer.index(r.id)
                        self.stdout.write(" - " + self.style.SUCCESS(f"added."))
                    else:
                        self.stdout.write('')
                    missing_meili += 1

            self.stdout.write(f'\r{missing_meili} {self.model._meta.verbose_name_plural} were missing from Meilisearch in total.')


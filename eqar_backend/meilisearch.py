# wrapper for Python meilisearch module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

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


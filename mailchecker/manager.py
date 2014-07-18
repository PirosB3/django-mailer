from oauth2client.file import Storage
from django.conf import settings
import mailer

from .query import ThreadQuerySet

class ThreadManager(object):
    def __init__(self, model):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()
        self.model = model

    def get_queryset(self):
        all_threads = mailer.get_all_threads(self.credentials)
        for t in all_threads:
            t._meta = self.model._meta
        return ThreadQuerySet(all_threads, credentials=self.credentials, model=self.model)

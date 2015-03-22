from oauth2client.file import Storage
from django.conf import settings
import mailer

from .query import ThreadQuerySet, MessageQuerySet


class GmailManager(object):

    def complex_filter(self, filter_obj):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def using(self, *args, **kwargs):
        return self

    def __init__(self, model):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()
        self.model = model


class ThreadManager(GmailManager):

    def get_queryset(self):
        all_threads = mailer.get_all_threads(self.credentials)
        for t in all_threads:
            t._meta = self.model._meta
        return ThreadQuerySet(all_threads, credentials=self.credentials,
                              model=self.model)


class MessageManager(GmailManager):

    def get_queryset(self):
        return MessageQuerySet([], credentials=self.credentials,
                               model=self.model)

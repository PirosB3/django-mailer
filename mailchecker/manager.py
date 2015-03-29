from oauth2client.file import Storage
from django.conf import settings
import mailer

from .query import ThreadQuerySet, MessageQuerySet


class GmailManager(object):

    def __init__(self, model):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()
        self.model = model

    def complex_filter(self, filter_obj):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def using(self, *args, **kwargs):
        return self

    def all(self):
        return self.get_queryset()

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get_queryset(self):
        return self.queryset(credentials=self.credentials,
                             model=self.model)

    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)


class ThreadManager(GmailManager):
    queryset = ThreadQuerySet


class MessageManager(GmailManager):
    queryset = MessageQuerySet

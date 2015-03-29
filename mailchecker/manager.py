from oauth2client.file import Storage
from django.conf import settings
import mailer

from .query import ThreadQuerySet, MessageQuerySet


class GmailManager(object):

    def __init__(self, model, **kwargs):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()
        self.model = model
        self.mailer = kwargs.get('mailer', mailer)
        self.initial_filter_query = kwargs.get('initial_filter_query', {})

    def complex_filter(self, filter_obj):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def using(self, *args, **kwargs):
        return self

    def iterator(self):
        return iter(self.get_queryset())

    def all(self):
        return self.get_queryset()

    def count(self):
        return len(self.get_queryset())

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get_queryset(self):
        return self.queryset(
            credentials=self.credentials,
            model=self.model,
            mailer=self.mailer,
            filter_query=self.initial_filter_query,
        )

    def get(self, *args, **kwargs):
        return self.get_queryset().get(*args, **kwargs)


class ThreadManager(GmailManager):
    queryset = ThreadQuerySet


class MessageManager(GmailManager):
    queryset = MessageQuerySet

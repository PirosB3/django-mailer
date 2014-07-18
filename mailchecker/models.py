from django.db.models.fields import AutoField, CharField, FieldDoesNotExist
from django.conf import settings

from oauth2client.file import Storage
import mailer


class ThreadOptions(object):
    abstract = False
    swapped = False
    app_label = 'mailchecker'
    model_name = 'thread'
    verbose_name = 'thread'
    verbose_name_raw = 'thread'
    verbose_name_plural = 'threads'
    object_name = 'thread'
    virtual_fields = []

    def __init__(self):

        self.af = AutoField()
        self.af.attname = 'id'
        self.af.name = 'id'

        self.number_of_messages = CharField(max_length=200)
        self.number_of_messages.attname = 'number_of_messages'
        self.number_of_messages.name = 'number_of_messages'

        self.pk = self.af

    def get_fields(self, m2m=False, data=True, related_m2m=False, related_objects=False, virtual=False,
                   include_parents=True, include_non_concrete=True, include_hidden=False, include_proxy=False, export_name_map=False):
        if data:
            return (self.af, self.number_of_messages)
        return tuple()

    def get_field(self, field_name, m2m=True, data=True, related_objects=False, related_m2m=False, virtual=True, **kwargs):
        if field_name == 'id':
            return self.af
        if field_name == 'number_of_messages':
            return self.number_of_messages
        raise FieldDoesNotExist()

    @property
    def many_to_many(self):
        return list(self.get_fields(data=False, m2m=True))

    @property
    def field_names(self):
        res = set()
        for _, names in self.get_fields(m2m=True, related_objects=True,
                                        related_m2m=True, virtual=True,
                                        export_name_map=True).iteritems():
            res.update(name for name in names if not name.endswith('+'))
        return list(res)

    @property
    def fields(self):
        return list(self.get_fields())

    @property
    def concrete_fields(self):
        return list(self.get_fields(include_non_concrete=False))

    @property
    def local_concrete_fields(self):
        return self.get_fields(include_parents=False, include_non_concrete=False)


class ThreadQuery(object):
    select_related = False
    order_by = tuple()


class ThreadQuerySet(list):
    def __init__(self, *args, **kwargs):
        self.credentials = kwargs.pop('credentials')
        super(ThreadQuerySet, self).__init__(*args, **kwargs)
        self.model = Thread
        self.query = ThreadQuery()

    def order_by(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def get(self, *args, **kwargs):
        thread_id = kwargs['pk']
        thread = mailer.get_thread_by_id(self.credentials, thread_id)
        thread._meta = self.model._meta
        return thread

    def _clone(self, *args, **kwargs):
        return self


class ThreadManager(object):
    def __init__(self):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

    def get_queryset(self):
        all_threads = mailer.get_all_threads(self.credentials)
        for t in all_threads:
            t._meta = Thread._meta
        return ThreadQuerySet(all_threads, credentials=self.credentials)

class Thread(object):
    _deferred = False

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name, m2m=True, related_objects=True,
                                         related_m2m=True, virtual=True)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

Thread._meta = ThreadOptions()
Thread._default_manager = ThreadManager()

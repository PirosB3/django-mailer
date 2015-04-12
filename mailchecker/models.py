from django.db.models.fields import FieldDoesNotExist
from django.db.models.base import ModelState

from .options import ThreadOptions, MessageOptions
from .manager import ThreadManager, MessageManager


class GmailModel(object):
    _deferred = False
    _state = ModelState()

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)

    @property
    def pk(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, GmailModel):
            return self.pk == other.pk
        return False

    def full_clean(self, *args, **kwargs):
        pass

    def validate_unique(self, *args, **kwargs):
        pass

    def _get_unique_checks(self, *args, **kwargs):
        return ([], [],)

    def _get_pk_val(self):
        return None


class constructor(type):
    def __new__(cls, name, bases, attrs):
        dm = attrs.pop('_default_manager')
        klass = super(constructor, cls).__new__(cls, name, bases, attrs)
        klass._default_manager = dm(klass)
        klass.objects = klass._default_manager
        return klass


class Message(GmailModel):
    __metaclass__ = constructor
    _default_manager = MessageManager
    _meta = MessageOptions()

    def __init__(self, id=None, receiver=None, sender=None, snippet=None,
                 body=None, thread=None, thread_id=None):
        self.id = id
        self.receiver = receiver
        self.sender = sender
        self.snippet = snippet
        self.body = body
        self.thread_id = thread_id

    @property
    def thread(self):
        return Thread.objects.get(id=self.thread_id)

    @thread.setter
    def thread(self, value):
        self.thread_id = value.id

    def __unicode__(self):
        return "<Message %s: '%s..'>" % (self.id, self.snippet[:30])

    def __repr__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):

        # Messages already save do not need re-sending
        if self.id:
            return

        # Send message and fetch ID
        result = self._default_manager.get_queryset()._create(
            frm=self.sender,
            to=self.receiver,
            message_body=self.body,
            thread_id=self.thread_id
        )

        # Not all results are returned from the API, re-pull and set
        # all fields (basically, reassigning the entire instance)
        new_instance = self._default_manager.get(pk=result['id'])
        for field_name in (f.name for f in self._meta.get_fields()):
            setattr(self, field_name, getattr(new_instance, field_name))


class Thread(GmailModel):
    __metaclass__ = constructor
    _default_manager = ThreadManager
    _meta = ThreadOptions()

    def __init__(self, id=None, to=None, number_of_messages=None):
        self.id = id
        self.to = to
        self.number_of_messages = number_of_messages

    @property
    def messages(self):
        return Message.objects.filter(thread=self.id)

    def __unicode__(self):
        return "<Thread %s with %s messages>" % (
            self.id,
            "???" if self.number_of_messages is None else self.number_of_messages
        )

    def __repr__(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        pass


Thread._meta._bind()
Message._meta._bind()

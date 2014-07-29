from django.db.models.fields import FieldDoesNotExist
import mailer

from .options import ThreadOptions, MessageOptions
from .manager import ThreadManager, MessageManager



class GmailModel(object):
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


class constructor(type):
    def __new__(cls, name, bases, attrs):
        dm = attrs.pop('_default_manager')
        klass = super(constructor, cls).__new__(cls, name, bases, attrs)
        klass._default_manager = dm(klass)
        return klass


class Message(GmailModel):
    __metaclass__ = constructor
    _default_manager = MessageManager
    _meta = MessageOptions()


class Thread(GmailModel):
    __metaclass__ = constructor
    _default_manager = ThreadManager
    _meta = ThreadOptions()

Thread._meta._bind()
Message._meta._bind()

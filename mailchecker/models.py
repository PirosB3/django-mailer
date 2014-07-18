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

class Thread(GmailModel):
    pass

class Message(GmailModel):
    pass

Thread._meta = ThreadOptions()
Thread._default_manager = ThreadManager(Thread)

Message._meta = MessageOptions()
Message._default_manager = MessageManager(Message)

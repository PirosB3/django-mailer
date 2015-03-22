from django.db.models.fields import (AutoField, CharField,
                                     FieldDoesNotExist, TextField)
from django.db.models import ForeignKey
from django.db.models.fields import FieldDoesNotExist
from django.db.models.options import CachedPropertiesMixin


class GmailAutoField(AutoField):
    concrete = True
    def to_python(self, value):
        return value


class GmailOptions(CachedPropertiesMixin):
    has_auto_field = True
    auto_created = False
    abstract = False
    swapped = False
    virtual_fields = []


class ThreadOptions(GmailOptions):
    auto_created = False
    app_label = 'mailchecker'
    model_name = 'thread'
    verbose_name = 'thread'
    verbose_name_raw = 'thread'
    verbose_name_plural = 'threads'
    object_name = 'thread'
    default_related_name = None

    def add_field(self, *args, **kwargs):
        pass

    def _bind(self):

        self.af = GmailAutoField()
        self.af.attname = 'id'
        self.af.name = 'id'

        self.number_of_messages = CharField(max_length=200)
        self.number_of_messages.attname = 'number_of_messages'
        self.number_of_messages.name = 'number_of_messages'

        self.number_of_messages.set_attributes_from_name('number_of_messages')
        self.af.set_attributes_from_name('af')

        self.pk = self.af

    def _get_fields(self, forward=True, reverse=True, include_parents=True,
                    include_hidden=False):
        from .models import Message
        from .models import Thread
        res = []
        if forward:
            res += [self.af, self.number_of_messages]
        if reverse:
            res += [Message._meta.get_field('thread').rel]
        return res

    def get_field(self, field_name):
        try:
            return next(f for f in self._get_fields()
                        if f.name == field_name)
        except StopIteration:
            raise FieldDoesNotExist()


class MessageOptions(GmailOptions):
    app_label = 'mailchecker'
    model_name = 'message'
    verbose_name = 'message'
    verbose_name_raw = 'message'
    verbose_name_plural = 'messages'
    object_name = 'message'
    default_related_name = None

    def add_field(self, *args, **kwargs):
        pass

    def _bind(self):
        self.af = GmailAutoField()
        self.af.attname = 'id'
        self.af.name = 'id'

        self.receiver = CharField(max_length=200)
        self.receiver.attname = 'receiver'
        self.receiver.name = 'receiver'

        self.sender = CharField(max_length=200)
        self.sender.attname = 'sender'
        self.sender.name = 'sender'

        self.body = TextField()
        self.body.attname = 'body'
        self.body.name = 'body'

        from .models import Thread, Message
        self.thread = ForeignKey(Thread)

        self.thread.contribute_to_class(Thread, 'thread')
        self.body.set_attributes_from_name('body')
        self.sender.set_attributes_from_name('sender')
        self.receiver.set_attributes_from_name('receiver')
        self.af.set_attributes_from_name('af')

        self.concrete_model = Message

        self.pk = self.af

    def _get_fields(self, reverse=True, forward=True):
        return (self.af, self.receiver, self.sender, self.body, self.thread)

    def get_field(self, field_name):
        m = {
            'id': self.af,
            'receiver': self.receiver,
            'sender': self.sender,
            'body': self.body,
            'thread': self.thread,
        }
        try:
            return m[field_name]
        except KeyError:
            raise FieldDoesNotExist()

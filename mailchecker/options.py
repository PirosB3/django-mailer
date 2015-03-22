from django.db.models.fields import (AutoField, CharField,
                                     FieldDoesNotExist, TextField)
from django.db.models import ForeignKey
from django.db.models.options import CachedPropertiesMixin


class GmailAutoField(AutoField):

    def to_python(self, value):
        return value


class GmailOptions(CachedPropertiesMixin):
    has_auto_field = True
    auto_created = False
    abstract = False
    swapped = False
    virtual_fields = []

    def __init__(self, *args, **kwargs):
        self._gmail_other_fields = {}

    def add_field(self, *args, **kwargs):
        pass

    def _bind(self):
        for field_name, field in self._gmail_fields.iteritems():
            setattr(self, field_name, field)
            field.set_attributes_from_name(field_name)
        self.pk = self._gmail_fields[self._gmail_pk_field]

    def _get_fields(self, reverse=True, forward=True):
        return tuple(
            field for field_name, field in
            sorted(list(self._gmail_fields.items()) +
                   list(self._gmail_other_fields.items()))
        )

    def get_field(self, field_name):
        try:
            return self._gmail_fields[field_name]
        except KeyError:
            try:
                return self._gmail_other_fields[field_name]
            except KeyError:
                raise FieldDoesNotExist()


class ThreadOptions(GmailOptions):
    auto_created = False
    app_label = 'mailchecker'
    model_name = 'thread'
    verbose_name = 'thread'
    verbose_name_raw = 'thread'
    verbose_name_plural = 'threads'
    object_name = 'thread'
    default_related_name = None

    _gmail_pk_field = 'id'
    _gmail_fields = {
        'id': GmailAutoField(),
        'number_of_messages': CharField(max_length=200),
    }


class MessageOptions(GmailOptions):
    app_label = 'mailchecker'
    model_name = 'message'
    verbose_name = 'message'
    verbose_name_raw = 'message'
    verbose_name_plural = 'messages'
    object_name = 'message'
    default_related_name = None

    _gmail_pk_field = 'id'
    _gmail_fields = {
        'id': GmailAutoField(),
        'receiver': CharField(max_length=200),
        'sender': CharField(max_length=200),
        'snippet': CharField(max_length=200),
        'body': TextField(),
    }

    def _bind(self):
        super(MessageOptions, self)._bind()

        from .models import Thread, Message
        self.thread = ForeignKey(Thread)
        self.thread.contribute_to_class(Thread, 'thread')
        self.concrete_model = Message
        self._gmail_other_fields['thread'] = self.thread

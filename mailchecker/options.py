from django.db.models.fields import AutoField, CharField, FieldDoesNotExist, TextField


class GmailAutoField(AutoField):

    def to_python(self, value):
        return value

class GmailOptions(object):
    abstract = False
    swapped = False
    virtual_fields = []


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


class ThreadOptions(GmailOptions):
    app_label = 'mailchecker'
    model_name = 'thread'
    verbose_name = 'thread'
    verbose_name_raw = 'thread'
    verbose_name_plural = 'threads'
    object_name = 'thread'

    def __init__(self):


        self.af = GmailAutoField()
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


class MessageOptions(GmailOptions):
    app_label = 'mailchecker'
    model_name = 'message'
    verbose_name = 'message'
    verbose_name_raw = 'message'
    verbose_name_plural = 'messages'
    object_name = 'message'

    def __init__(self):
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

        self.pk = self.af


    def get_fields(self, m2m=False, data=True, related_m2m=False, related_objects=False, virtual=False,
                   include_parents=True, include_non_concrete=True, include_hidden=False, include_proxy=False, export_name_map=False):
        if data:
            return (self.af, self.receiver, self.sender, self.body)
        return tuple()

    def get_field(self, field_name, m2m=True, data=True, related_objects=False, related_m2m=False, virtual=True, **kwargs):
        if data:
            m = {
                'id': self.af,
                'receiver': self.receiver,
                'sender': self.sender,
                'body': self.body,
            }
            try:
                return m[field_name]
            except KeyError:
                pass
        raise FieldDoesNotExist()

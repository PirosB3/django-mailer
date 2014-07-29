import mailer


class GmailQuery(object):
    select_related = False
    order_by = tuple()


class GmailQuerySet(list):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.credentials = kwargs.pop('credentials')
        super(GmailQuerySet, self).__init__(*args, **kwargs)
        self.query = GmailQuery()

    def order_by(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def _clone(self, *args, **kwargs):
        return self


class ThreadQuerySet(GmailQuerySet):

    def get(self, *args, **kwargs):
        thread_id = kwargs['pk']
        thread = mailer.get_thread_by_id(self.credentials, thread_id)
        thread._meta = self.model._meta
        return thread


class MessageQuerySet(GmailQuerySet):

    def get(self, *args, **kwargs):
        message_id = kwargs['pk']
        message = mailer.get_message_by_id(self.credentials, message_id)
        message._meta = self.model._meta
        return message

import mailer


class ThreadQuery(object):
    select_related = False
    order_by = tuple()


class ThreadQuerySet(list):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.credentials = kwargs.pop('credentials')
        super(ThreadQuerySet, self).__init__(*args, **kwargs)
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

import mailer


class GmailQuery(object):
    select_related = False
    order_by = tuple()


class GmailQuerySet(object):

    def using(self, db):
        return self

    def __init__(self, *args, **kwargs):
        self._cache = None
        self.ordered = True
        self.model = kwargs.pop('model')
        self.credentials = kwargs.pop('credentials')
        self.mailer = kwargs.pop('mailer', mailer)
        self.filter_query = kwargs.pop('filter_query', None)
        self.query = GmailQuery()

    def order_by(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def _clone(self, *args, **kwargs):
        return self

    def count(self):
        return len(self._get_data())

    def __getitem__(self, k):
        return self._get_data()[k]

    def all(self):
        return self._get_data()

    def _set_model_attrs(self, instance):
        instance._meta = self.model._meta
        instance._state = self.model._state
        return instance


class ThreadQuerySet(GmailQuerySet):

    def get(self, *args, **kwargs):
        thread_id = kwargs['id']
        thread = self.mailer.get_thread_by_id(self.credentials,
                                              thread_id)
        return self._set_model_attrs(thread)

    def _get_data(self):
        if not self._cache:
            to = self.filter_query['to__icontains'] if self.filter_query else None
            all_threads = self.mailer.get_all_threads(self.credentials, to=to)
            self._cache = map(self._set_model_attrs, all_threads)
        return self._cache

    def filter(self, *args, **kwargs):
        filter_args = kwargs if kwargs else {}
        if len(args) > 0:
            filter_args.update(dict(args[0].children))
        if 'to__icontains' in filter_args:
            return ThreadQuerySet(
                model=self.model,
                credentials = self.credentials,
                mailer = self.mailer,
                filter_query = {'to__icontains': filter_args['to__icontains']}
            )
        return self


class MessageQuerySet(GmailQuerySet):

    def __init__(self, *args, **kwargs):
        self.selected_thread = kwargs.pop('selected_thread', None)
        super(MessageQuerySet, self).__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        selected_thread = kwargs.pop('thread', None)
        if selected_thread:
            return MessageQuerySet(
                model=self.model,
                credentials=self.credentials,
                selected_thread=selected_thread
            )
        return self


    def __len__(self):
        return len([k for k in self])

    def __getitem__(self, n):
        return [k for k in self][n]

    def __iter__(self):
        try:
            return iter(self._cache)
        except AttributeError:
            pass

        if not self.selected_thread:
            return super(MessageQuerySet, self).__iter__()

        messages = mailer.get_messages_by_thread_id(
            self.credentials,
            self.selected_thread.id
        )
        for m in messages:
            m._meta = self.model._meta
            m._state = self.model._state
        self._cache = messages
        return iter(messages)

    def get(self, *args, **kwargs):
        message_id = kwargs['pk']
        message = mailer.get_message_by_id(self.credentials, message_id)
        message._meta = self.model._meta
        return message

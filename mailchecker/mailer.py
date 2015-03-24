import httplib2
from apiclient.discovery import build

import base64
from django.db.models.fields import FieldDoesNotExist

ME = 'me'


class Bunch(object):
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs
        self.pk = self.id

    def __unicode__(self):
        return self.id

    def serializable_value(self, field_name):
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)


def _get_gmail_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def _make_message(msg):
    try:
        parts = [p['body'] for p in msg['payload']['parts']]
    except KeyError:
        parts = [msg['payload']['body']]

    body = ''.join(base64.urlsafe_b64decode(p['data'].encode('utf-8'))
                   for p in parts if 'data' in p)
    sender = [h['value'] for h in msg['payload']['headers']
              if h['name'] == 'From'][0]
    receiver = [h['value'] for h in msg['payload']['headers']
                if h['name'] == 'To'][0]
    return Bunch(
        id=msg['id'],
        thread_id=msg['threadId'],
        snippet=msg['snippet'],
        receiver=receiver,
        sender=sender,
        body=body
    )


def get_messages_by_thread_id(credentials, thread_id):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()

    return map(_make_message, thread['messages'])


def get_all_threads(credentials, to=None):
    gmail = _get_gmail_service(credentials)
    params = {
        'userId': ME,
    }
    if to:
        params['q'] = 'to:%s' % to
    threads = gmail.users().threads().list(**params).execute()
    if not threads or threads['resultSizeEstimate'] is 0:
        return tuple()
    return tuple(Bunch(id=t['id'], number_of_messages=None) for t in threads['threads'])


def get_all_messages(credentials):
    gmail = _get_gmail_service(credentials)
    messages = gmail.users().messages().list(
        userId=ME,
    ).execute()['messages']
    return tuple(_make_message(m) for m in messages)


def get_thread_by_id(credentials, thread_id):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()
    return Bunch(
        id=thread['id'],
        number_of_messages=len(thread['messages'])
    )


def get_message_by_id(credentials, message_id):
    gmail = _get_gmail_service(credentials)
    message = gmail.users().messages().get(
        userId=ME,
        id=message_id
    ).execute()
    return _make_message(message)

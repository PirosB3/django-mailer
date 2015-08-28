import httplib2
from apiclient.discovery import build
from email.mime.text import MIMEText

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


def _make_message(msg, cls):
    try:
        parts = [p['body'] for p in msg['payload']['parts']]
    except KeyError:
        parts = [msg['payload']['body']]

    body = ''.join(base64.urlsafe_b64decode(p['data'].encode('utf-8'))
                   for p in parts if 'data' in p)
    sender = [h['value'] for h in msg['payload']['headers']
              if h['name'].lower() in 'from'][0]
    receiver = [h['value'] for h in msg['payload']['headers']
                if h['name'].lower() == 'to'][0]
    return cls(
        id=msg['id'],
        thread_id=msg['threadId'],
        snippet=msg['snippet'],
        receiver=receiver,
        sender=sender,
        body=body
    )


def send_message(credentials, frm, to, message_body, subject="Hello from Pycon", thread_id=None):
    gmail = _get_gmail_service(credentials)
    message = MIMEText(message_body)
    message['to'] = to
    message['from'] = frm
    message['subject'] = subject

    payload = {'raw': base64.b64encode(message.as_string())}
    if thread_id:
        payload['threadId'] = thread_id
    return gmail.users().messages().send(
        userId=ME,
        body=payload,
    ).execute()

def get_messages_by_thread_id(credentials, thread_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()

    return [_make_message(m, cls) for m in thread['messages']]


def get_all_threads(credentials, to=None, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    params = {
        'userId': ME,
    }
    if to:
        params['q'] = 'to:%s' % to
    threads = gmail.users().threads().list(**params).execute()
    if not threads or (to != None and threads['resultSizeEstimate'] is 0):
        return tuple()
    return tuple(cls(id=t['id'], number_of_messages=None, to=None)
                 for t in threads['threads'])


def get_all_messages(credentials, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    messages = gmail.users().messages().list(
        userId=ME,
    ).execute()['messages']
    return [_make_message(m, cls) for m in messages]


def get_thread_by_id(credentials, thread_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    thread = gmail.users().threads().get(
        userId=ME,
        id=thread_id
    ).execute()
    return cls(
        id=thread['id'],
        to=None,
        number_of_messages=len(thread['messages'])
    )


def get_message_by_id(credentials, message_id, cls=Bunch):
    gmail = _get_gmail_service(credentials)
    message = gmail.users().messages().get(
        userId=ME,
        id=message_id
    ).execute()
    return _make_message(message, cls)

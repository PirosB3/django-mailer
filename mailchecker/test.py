import unittest
import mailer

from django.conf import settings
from oauth2client.file import Storage

from .models import Thread, Message
from .query import ThreadQuerySet
import mock
from mailer import Bunch

class ThreadQuerySetTestCase(unittest.TestCase):

    def setUp(self):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

    def test_queryset(self):
        mailer = mock.MagicMock()
        mailer.get_all_threads.return_value = [
            Bunch(id='1'),
            Bunch(id='2'),
            Bunch(id='3'),
        ]

        tqs = ThreadQuerySet(
            model=Thread,
            credentials = self.credentials,
            mailer = mailer
        )
        self.assertEqual(tqs.count(), 3)
        self.assertEqual(tqs[1].id, '2')
        self.assertTrue([
            model._meta
            for model in tqs.all()
        ])

class ThreadTestCase(unittest.TestCase):

    def test_thread_select_all(self):
        threads = Thread.objects.all()
        self.assertTrue(len(threads) > 0)
        for thread in threads:
            self.assertTrue(thread._meta)
            self.assertTrue(thread.id)


class MailerTestCase(unittest.TestCase):

    def setUp(self):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

    def test_can_get_all_threads_with_to_filter(self):
        threads = mailer.get_all_threads(self.credentials,
                                         to='shogun-list@shogun-toolbox.org')
        self.assertTrue(threads)
        self.assertTrue(all(len(t.id) > 1 for t in threads))

    def test_can_get_all_threads(self):
        threads = mailer.get_all_threads(self.credentials)
        self.assertTrue(threads)
        self.assertTrue(all(len(t.id) > 1 for t in threads))

    def test_can_get_a_thread(self):
        thread_id = '1474404b4b594fea'
        thread = mailer.get_thread_by_id(self.credentials, thread_id)
        self.assertEqual(thread.id, thread_id)
        self.assertEqual(thread.number_of_messages, 1)

    def test_can_get_all_messages_of_a_thread(self):
        thread_id = '1474404b4b594fea'
        messages = mailer.get_messages_by_thread_id(self.credentials, thread_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].id, '1474404b4b594fea')
        self.assertEqual(messages[0].sender, 'Camilla <camillamon@gmail.com>')
        self.assertEqual(messages[0].receiver, 'shogun-list <shogun-list@shogun-toolbox.org>')
        self.assertTrue(messages[0].body.startswith('Hello everyone'))

    def test_can_get_message_by_id(self):
        message_id = '1474404b4b594fea'
        message = mailer.get_message_by_id(self.credentials, message_id)
        self.assertEqual(message.id, '1474404b4b594fea')
        self.assertEqual(message.sender, 'Camilla <camillamon@gmail.com>')
        self.assertEqual(message.receiver, 'shogun-list <shogun-list@shogun-toolbox.org>')
        self.assertTrue(message.body.startswith('Hello everyone'))

if __name__ == '__main__':
    unittest.main()

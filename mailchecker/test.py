import unittest
import mailer

from django.conf import settings
from django.db.models import Q
from oauth2client.file import Storage

from .models import Thread, Message
from .query import ThreadQuerySet, MessageQuerySet
import mock
from mailer import Bunch


class MessageTestCase(unittest.TestCase):

    def setUp(self):
        self.mailer = mock.MagicMock()
        self._old_mailer = Thread._default_manager.mailer

        Message._default_manager.mailer = self.mailer
        Thread._default_manager.mailer = self.mailer

    def tearDown(self):
        Message._default_manager.mailer = self._old_mailer
        Thread._default_manager.mailer = self._old_mailer

    def test_reverse_relation_works(self):
        self.mailer.get_thread_by_id.return_value = Message(
            id="00126"
        )
        t = Message(id="00125")
        self.assertEqual(t.thread.id, "00126")
        self.assertEqual(
            self.mailer.get_thread_by_id.call_args[0][1],
            '00125'
        )


class MessageQuerySetTestCase(unittest.TestCase):

    def setUp(self):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()
        self.mailer = mock.MagicMock()

    def test_message_with_filter(self):
        self.mailer.get_messages_by_thread_id.return_value = [
            Bunch(id='1'),
        ]
        mqs = MessageQuerySet(
            model=Message,
            credentials=self.credentials,
            mailer=self.mailer
        )
        self.assertEqual(mqs.filter(thread='1')[0].pk, '1')
        self.assertEqual(
            self.mailer.get_messages_by_thread_id.call_args[0][1],
            '1'
        )

    def test_message_with_id(self):
        self.mailer.get_message_by_id.return_value = Bunch(id='1')
        mqs = MessageQuerySet(
            model=Message,
            credentials=self.credentials,
            mailer=self.mailer
        )
        self.assertEqual(mqs.get(pk='1843903').pk, '1')
        self.assertEqual(
            self.mailer.get_message_by_id.call_args[0][1],
            '1843903'
        )


class ThreadQuerySetTestCase(unittest.TestCase):

    def setUp(self):
        self.mailer = mock.MagicMock()
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

    def test_queryset(self):
        self.mailer.get_all_threads.return_value = [
            Bunch(id='1'),
            Bunch(id='2'),
            Bunch(id='3'),
        ]

        tqs = ThreadQuerySet(
            model=Thread,
            credentials=self.credentials,
            mailer=self.mailer
        )
        self.assertEqual(tqs.count(), 3)
        self.assertEqual(tqs[1].id, '2')
        self.assertTrue([
            model._meta
            for model in tqs.all()
        ])

    def test_queryset_get(self):
        self.mailer.get_thread_by_id.return_value = Bunch(id='target')
        tqs = ThreadQuerySet(
            model=Thread,
            credentials = self.credentials,
            mailer=self.mailer
        )
        self.assertEqual(tqs.get(id='target').id, 'target')
        self.assertEqual(
            self.mailer.get_thread_by_id.call_args[0][1],
            'target'
        )

    def test_queryset_filter(self):
        self.mailer.get_all_threads.return_value = [
            Bunch(id='target1'),
            Bunch(id='target2'),
        ]
        tqs = ThreadQuerySet(
            model=Thread,
            credentials=self.credentials,
            mailer=self.mailer
        )
        tqs2 = tqs.filter(to__icontains="daniel@gmail.com")
        self.assertNotEqual(tqs, tqs2)

        self.assertEqual(
            [b.id for b in tqs2.all()],
            ['target1', 'target2']
        )
        self.assertEqual(
            self.mailer.get_all_threads.call_args_list[0][1]['to'],
            'daniel@gmail.com'
        )

    def test_queryset_filter_Q(self):
        self.mailer.get_all_threads.return_value = [
            Bunch(id='target1'),
            Bunch(id='target2'),
        ]
        tqs = ThreadQuerySet(
            model=Thread,
            credentials = self.credentials,
            mailer=self.mailer
        )
        query = Q(to__icontains="daniel@gmail.com")
        tqs2 = tqs.filter(query)
        self.assertEqual(
            [b.id for b in tqs2.all()],
            ['target1', 'target2']
        )
        self.assertEqual(
            self.mailer.get_all_threads.call_args_list[0][1]['to'],
            'daniel@gmail.com'
        )


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

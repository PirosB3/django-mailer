import unittest
import mailer

from django.conf import settings
from django.db.models import Q
from oauth2client.file import Storage

from .models import Thread, Message
from .query import ThreadQuerySet, MessageQuerySet
import mock
from mailer import Bunch


class ThreadTestCase(unittest.TestCase):

    def setUp(self):
        self.mailer = mock.MagicMock()
        self._old_mailer = Thread._default_manager.mailer

        Message._default_manager.mailer = self.mailer
        Thread._default_manager.mailer = self.mailer

    def tearDown(self):
        Message._default_manager.mailer = self._old_mailer
        Thread._default_manager.mailer = self._old_mailer

    def test_reverse_relation_lookup(self):
        self.mailer.get_messages_by_thread_id.return_value = [
            Bunch(id=str(n)) for n in xrange(10)
        ]
        t = Thread(id='123123')
        self.assertEqual(t.messages.count(), 10)


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


if __name__ == '__main__':
    unittest.main()

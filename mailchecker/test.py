import unittest
import mailer

from django.conf import settings

from oauth2client.file import Storage


class MailerTestCase(unittest.TestCase):

    def setUp(self):
        storage = Storage(settings.CREDENTIALS_PATH)
        self.credentials = storage.get()

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

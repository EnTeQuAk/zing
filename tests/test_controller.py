#-*- coding: utf-8 -*-
import unittest
from boto.sqs.connection import SQSConnection
from moto import mock_sqs
from zing.controller import Controller, get_sqs_region
from zing.message import EventMessage


class TestControllerUtils(unittest.TestCase):
    def test_region(self):
        region = get_sqs_region('us-east-1')
        self.assertEqual(region.name, 'us-east-1')


class TestController(unittest.TestCase):

    def _create_queue(self, name):
        sqs = SQSConnection(region=get_sqs_region('us-east-1'))
        self.assertEqual(len(sqs.get_all_queues()), 0)
        queue = sqs.create_queue(name)
        return queue

    @mock_sqs
    def test_controller_fetches_queue_on_init(self):
        ctrl = Controller()
        self.assertEqual(ctrl.get_queues(), {})

        self._create_queue('test-events')

        ctrl = Controller()
        self.assertEqual(ctrl._queue_cache.keys(), ['test-events'])

    def test_normalize_queue_name(self):
        self.assertEqual(
            Controller().normalize_queue_name('prefix.name'),
            'prefix-name'
        )

        self.assertEqual(
            Controller().normalize_queue_name('prefix!{name}'),
            'prefix__name_'
        )

        self.assertEqual(
            Controller().normalize_queue_name('prefix.{name}'),
            'prefix-_name_'
        )

    @mock_sqs
    def test_get_queue(self):
        ctrl = Controller()
        queue = ctrl.get_queue('events', prefix='test', visibility_timeout=20)
        self.assertEqual(queue.name, 'test-events')
        self.assertEqual(queue.get_timeout(), 20)
        self.assertEqual(queue.message_class, EventMessage)
        self.assertEqual(
            ctrl._queue_cache,
            {'test-events': queue}
        )

    @mock_sqs
    def test_get_queues(self):
        ctrl = Controller()
        self.assertEqual(ctrl.get_queues(), {})
        self._create_queue('test')
        self.assertEqual(ctrl.get_queues().keys(), ['test'])

    @mock_sqs
    def test_get_and_send_messages(self):
        ctrl = Controller()
        ctrl.send_message('events', 'topic', 'subject')
        self.assertEqual(
            ctrl.get_messages('events')[0].get_body(),
            {
                'topic': 'topic',
                'subject': 'subject',
                'options': {}
            }
        )

    @mock_sqs
    def test_ack_message(self):
        ctrl = Controller()
        ctrl.send_message('events', 'topic', 'subject')

        queue = ctrl.get_queue('events')
        self.assertEqual(queue.count(), 1)

        message = ctrl.get_messages('events')[0]
        ctrl.ack_message(message, 'events')

        self.assertEqual(queue.count(), 0)

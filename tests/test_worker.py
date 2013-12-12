#-*- coding: utf-8 -*-
import time
import unittest
import gevent
from contextlib import contextmanager
from textwrap import dedent
import boto
from moto import mock_sqs, mock_ec2
from boto.sqs.connection import SQSConnection
from zing.worker import Worker
from zing.controller import get_sqs_region
from zing import consumers
from zing.message import make_message

from gevent import monkey
monkey.patch_all()


def dummy_consumer(ctrl, message):
    return message


@contextmanager
def spawn_worker(worker):
    greenlet = gevent.spawn(worker.run)

    yield

    greenlet.kill(block=True)


class TestWorker(unittest.TestCase):

    @mock_sqs
    def test_empty_worker(self):
        sqs = SQSConnection(region=get_sqs_region('us-east-1'))

        self.assertEqual(len(sqs.get_all_queues()), 0)

        with spawn_worker(Worker()):
            # Worker is empty, not registering any queues
            self.assertEqual(len(sqs.get_all_queues()), 0)

    @mock_sqs
    def test_worker_creates_queue(self):
        sqs = SQSConnection(region=get_sqs_region('us-east-1'))

        self.assertEqual(len(sqs.get_all_queues()), 0)

        worker = Worker()
        worker.ctrl.wait_time_seconds = 0.1
        worker.idle_time_seconds = 0.1
        worker.add_consumer('test_events', dummy_consumer)

        with spawn_worker(worker):
            time.sleep(.2)
            all_queues = sqs.get_all_queues()
            self.assertEqual(len(all_queues), 1)

            self.assertEqual(
                all_queues[0].name,
                'test_events'
            )

    @mock_sqs
    def test_worker_consumes_queue(self):
        sqs = SQSConnection(region=get_sqs_region('us-east-1'))

        self.assertEqual(len(sqs.get_all_queues()), 0)

        queue = sqs.create_queue('test_events')

        queue.write(make_message({'test': '1'}))

        self.assertEqual(queue.count(), 1)

        worker = Worker()
        worker.ctrl.wait_time_seconds = 0.1
        worker.idle_time_seconds = 0.1
        worker.add_consumer('test_events', dummy_consumer)

        with spawn_worker(worker):
            time.sleep(.2)
            self.assertEqual(queue.count(), 0)

            queue.write(make_message({'test': '2'}))

            self.assertEqual(queue.count(), 1)

            time.sleep(.2)

            self.assertEqual(queue.count(), 0)

#-*- coding: utf-8 -*-
"""
    zing.worker
    ~~~~~~~~~~~~~~~~~

    The worker thread that consumes a queue.
"""
import gevent

from gevent import monkey
monkey.patch_all()

import gevent.hub
from gevent.pool import Pool

from zing.controller import Controller


class Worker(object):

    # Time the consumer is able to sleep if there are no messages.
    # Depends on the real-time factor but keep this value high if possible
    # to reduce load and cost.
    idle_time_seconds = 5

    def __init__(self):
        self.ctrl = Controller()

        # We assume that we have less than 1000 queues here.
        # TODO: ``group`` might make more sense, does it?
        self.pool = Pool(1000)

        self.consumers = {}

    def consume(self, queue_name, prefix=None):
        while True:
            messages = self.ctrl.get_messages(queue_name, prefix, limit=1)
            if messages:
                message = messages[0]

                # Process the message by all consumers. On success
                # acknowledge the message. In case of an error
                # the message is again available on the queue after
                # a short period of time.
                for _, consumer in self.consumers[queue_name]:
                    consumer(self.ctrl, message)
                self.ctrl.ack_message(message, queue_name, prefix)
            else:
                gevent.sleep(self.idle_time_seconds)

    def add_consumer(self, queue_name, consumer, prefix=None):
        # Register a queue first
        self.ctrl.get_queue(queue_name, prefix)
        self.consumers.setdefault(queue_name, []).append((prefix, consumer))

    def run(self):
        self.running = True

        try:
            for queue_name in self.consumers:
                for prefix, consumer in self.consumers[queue_name]:
                    self.pool.spawn(self.consume, queue_name, prefix)

            while self.running:
                # allow fast context switching
                gevent.sleep(self.idle_time_seconds)
        finally:
            self.pool.kill()

    def stop(self):
        self.running = False
        gevent.sleep(self.idle_time_seconds)
        self.pool.kill()

#-*- coding: utf-8 -*-
"""
    zing.controller
    ~~~~~~~~~~~~~~~~~~~~~

    The controller that wraps all basic functionality. It's possible
    to expose the controller via `zerorpc <http://zerorpc.dotcloud.com/>`_
    and in terms of stream the controller is opinionated.

    The controller implements the following basic functionalities:

     * Wrap basic SQS functionality to easily communicate with
       a variety of services.

    Probably in the future the controller will implement a variety
    of functionality to work with AWS and to query different
    information.
"""
import string

import boto
import boto.sqs
from boto.vpc import VPCConnection
from boto.sqs.connection import SQSConnection

from django.conf import settings

from zing.message import EventMessage, make_message
from zing.conf import settings

# dots are replaced by dash, all other punctuation
# replaced by underscore.
CHARS_REPLACE_TABLE = dict((ord(c), 0x5f)
                           for c in string.punctuation if c not in '-_.')
CHARS_REPLACE_TABLE[0x2e] = 0x2d  # '.' -> '-'


def get_sqs_region(region_name):
    """Helper to get the proper region object."""
    for region in boto.sqs.regions():
        if region.name == region_name:
            return region


class Controller(object):
    """Controller to export various functionalities regarding AWS in general."""

    def __init__(self):
        credentials = {
            'aws_access_key_id': settings.ZING_AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.ZING_AWS_SECRET_ACCESS_KEY
        }

        region = settings.ZING_AWS_REGION

        self.sqs = SQSConnection(region=get_sqs_region(region), **credentials)
        self.vpc = VPCConnection(**credentials)
        self.ec2 = boto.connect_ec2(**credentials)

        self._queue_cache = {}

        # Populate the queue cache.
        self.get_queues()

        # Time to be used for keep-alive queue polling. This effectively
        # reduces the amount of poll requests, cost and improves efficiency.
        self.wait_time_seconds = settings.ZING_SQS_WAIT_TIME_SECONDS

    def normalize_queue_name(self, name, prefix=None, table=CHARS_REPLACE_TABLE):
        """Normalize an queue name into a legal SQS queue name.

        .. note::

            Normalize all queue access for consistency with initial
            ``Controller._queue_cache`` population.

        Reference: http://aws.amazon.com/sqs/faqs/#Are_there_name_restrictions
        """
        if prefix is not None:
            name = '{}.{}'.format(prefix, name)

        return unicode(name).translate(table)

    def get_queue(self, queue_name, prefix=None, visibility_timeout=None):
        """Get a :cls:`~boto.sqs.queue.Queue`object.

        If a queue does not exist it will be created.

        .. note::

            The message class is set to :cls:`zing.message.EventMessage`.
        """
        queue_name = self.normalize_queue_name(queue_name, prefix)

        try:
            queue = self._queue_cache[queue_name]
        except KeyError:
            queue = self.sqs.get_queue(queue_name)
            if queue is None:
                queue = self.sqs.create_queue(
                    queue_name,
                    visibility_timeout,
                )
            self._queue_cache[queue_name] = queue

        queue.set_message_class(EventMessage)
        return queue

    def get_queues(self):
        """Returns all queues known to the controller.

        Updates the queue cache!

        :returns: A dictionary of (name, queue_object).
        """
        # SQS blows up when you try to create a new queue if one already
        # exists with a different visibility_timeout, so this prepopulates
        # the queue_cache to protect us from recreating queues that
        # are known to already exist.
        # NOTE: Does *not* filter by prefix but only by SQS account.

        queues = self.sqs.get_all_queues()
        for queue in queues:
            self._queue_cache[queue.name] = queue

        return self._queue_cache

    def get_messages(self, queue_name, prefix=None, limit=1):
        """Get ``limit`` messages from ``queue_name``.

        .. warning::

            This method blocks for ``wait_time_seconds``!
        """
        queue = self.get_queue(queue_name, prefix)
        result = queue.get_messages(limit, wait_time_seconds=self.wait_time_seconds)
        return result

    def ack_message(self, message, queue_name, prefix=None):
        """Acknowledge ``message`` on ``queue_name``.

        This method deletes the message from the queue.
        """
        queue = self.get_queue(queue_name, prefix)
        queue.delete_message(message)

    def send_message(self, queue_name, topic, subject, prefix=None, **options):
        message = {
            'topic': topic,
            'subject': subject,
            'options': options
        }

        queue = self.get_queue(queue_name, prefix)

        queue.write(make_message(message))

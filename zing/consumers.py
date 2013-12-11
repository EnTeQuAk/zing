#-*- coding: utf-8 -*-
"""
    zing.consumers
    ~~~~~~~~~~~~~~

    Consumer definitions for the AWS zing.
"""

import boto


def consume_events(ctrl, message):
    """Consume events."""
    data = message.get_body()


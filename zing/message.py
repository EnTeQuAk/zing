import base64

from boto.sqs.message import MHMessage
from boto.exception import SQSDecodeError
from boto.compat import json


def make_message(value):
    msg = EventMessage()
    msg.set_body(value)
    return msg


class EventMessage(MHMessage):
    """
    Acts like a dictionary but encodes it's data as a Base64 encoded JSON payload.
    """

    def decode(self, value):
        try:
            value = base64.b64decode(value)
            value = json.loads(value)
        except Exception as exc:
            raise SQSDecodeError('Unable to decode message %s' % exc, self)
        return value

    def encode(self, value):
        value = json.dumps(value)
        return base64.b64encode(value)

#-*- coding: utf-8 -*-
import unittest
from zing.message import make_message, EventMessage

from boto.exception import SQSDecodeError


class TestMessage(unittest.TestCase):

    def test_message_decode(self):
        msg = EventMessage()
        self.assertEqual(
            msg.decode('eyJ0ZXN0IjogIm1zZyJ9'),
            {'test': 'msg'}
        )

    def test_message_decode_raises(self):
        msg = EventMessage()
        self.assertRaises(SQSDecodeError, msg.decode, object())

    def test_message_encode(self):
        msg = EventMessage()
        self.assertEqual(
            msg.encode({'test': 'msg'}),
            'eyJ0ZXN0IjogIm1zZyJ9'
        )

    def test_make_message(self):
        msg = make_message({'test': 'msg'})
        self.assertEqual(
            msg.get_body(),
            {'test': 'msg'}
        )

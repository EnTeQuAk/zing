#-*- coding: utf-8 -*-
"""
    zing.conf
    ~~~~~~~~~

    Holds configuration values.
"""
from django.conf import settings
from appconf import AppConf


class ZingConf(AppConf):
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None
    AWS_REGION = 'us-east-1'
    SQS_WAIT_TIME_SECONDS = 20

    class Meta:
        prefix = 'zing'

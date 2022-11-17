# coding=utf-8
import time

from aliyun_sdk_secretsmanager_common_plugin.utils import date_utils


class MonitorMessageInfo(object):

    def __init__(self, action, secret_name, access_key_id, error_message, alarm=False):
        self.action = action
        self.secret_name = secret_name
        self.access_key_id = access_key_id
        self.error_message = error_message
        self.alarm = alarm
        self.timestamp = date_utils.format_date(time.time(), date_utils.TIMEZONE_DATE_PATTERN)

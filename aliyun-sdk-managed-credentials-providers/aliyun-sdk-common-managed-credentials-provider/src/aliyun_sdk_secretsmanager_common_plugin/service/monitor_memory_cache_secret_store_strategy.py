# coding=utf-8
import json
import random
import time

from alibaba_cloud_secretsmanager_client.utils import common_logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_STOPPED

from aliyun_sdk_secretsmanager_common_plugin.model.monitor_message_info import MonitorMessageInfo
from aliyun_sdk_secretsmanager_common_plugin.service.monitor_cache_secret_store_strategy import \
    MonitorCacheSecretStoreStrategy
from aliyun_sdk_secretsmanager_common_plugin.utils import consts, monitor_message_utils


def judge_secret_expired(rotation_interval, refresh_timestamp):
    if rotation_interval is None or rotation_interval == "":
        raise ValueError("rotation interval is null")
    interval = int(rotation_interval.replace("s", "")) * 1000
    if rotation_interval is None or rotation_interval == "":
        raise ValueError("rotation interval is invalid")
    return interval + int(round(time.time() * 1000)) < refresh_timestamp


class MonitorMemoryCacheSecretStoreStrategy(MonitorCacheSecretStoreStrategy):

    def __init__(self, queue, monitor_period, monitor_customer_period):
        self.queue = queue
        self.monitor_period = monitor_period
        self.monitor_customer_period = monitor_customer_period
        self.cache_map = {}
        self.monitor = self.SecretsManagerPluginMonitor(queue, self.cache_map, monitor_period,
                                           monitor_customer_period)

    def add_refresh_hook(self, secret_cache_client):
        self.monitor.init_secret_cache_client(secret_cache_client)

    def init(self):
        self.monitor.init()

    def store_secret(self, cache_secret_info):
        self.cache_map[cache_secret_info.secret_info.secret_name] = cache_secret_info

    def get_cache_secret_info(self, secret_name):
        return self.cache_map.get(secret_name)

    def close(self):
        if self.cache_map is not None:
            self.cache_map.clear()
        if self.monitor is not None:
            self.monitor.close()

    class SecretsManagerPluginMonitor(object):
        DEFAULT_MONITOR_PERIOD = 30 * 60 * 1000
        DEFAULT_SEND_PERIOD = 120 * 60 * 1000

        def __init__(self, queue, cache_map,
                     monitor_period, send_period):
            self.queue = queue
            self.sched = None
            self.secret_cache_client = None
            self.monitor_period = monitor_period
            self.send_period = send_period
            self.cache_map = cache_map

        def init_secret_cache_client(self, secret_cache_client):
            self.secret_cache_client = secret_cache_client

        def init(self):
            if self.monitor_period is None or self.monitor_period < self.DEFAULT_MONITOR_PERIOD:
                self.monitor_period = self.DEFAULT_MONITOR_PERIOD
            if self.send_period is None or self.send_period < self.DEFAULT_SEND_PERIOD:
                self.send_period = self.DEFAULT_SEND_PERIOD
            self.sched = BackgroundScheduler()
            start = int(round(time.time() * 1000)) + random.randint(0, self.DEFAULT_MONITOR_PERIOD)
            self.sched.add_job(self.monitor, 'interval',
                               next_run_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start / 1000)),
                               seconds=self.monitor_period / 1000)
            self.sched.add_job(self.consume_message, 'interval',
                               next_run_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start / 1000)),
                               seconds=self.send_period / 1000)
            self.sched.start()

        def __del__(self):
            self.close()

        def close(self):
            if self.sched is not None and self.sched.state != STATE_STOPPED:
                self.sched.shutdown()

        def monitor(self):
            try:
                for secret_name in self.cache_map.keys():
                    self.monitor_ak_status(secret_name)
            except Exception as e:
                monitor_message_utils.add_message(self.queue,
                                                  MonitorMessageInfo(consts.MONITOR_AK_STATUS_ACTION,
                                                                     None, None, str(e), True))

        def monitor_ak_status(self, secret_name):
            secret_info = self.secret_cache_client.get_secret_info(secret_name)
            if (secret_info.secret_type is not None or secret_info.secret_type != "") and \
                    consts.RAM_CREDENTIALS_SECRET_TYPE.upper() == secret_info.secret_type.upper():
                extended_config = secret_info.extended_config
                if extended_config is not None:
                    extended_config_dict = json.loads(extended_config)
                    secret_sub_type = extended_config_dict.get(consts.EXTENDED_CONFIG_PROPERTY_SECRET_SUB_TYPE, "")
                    if consts.RAM_USER_ACCESS_KEY_SECRET_SUB_TYPE == secret_sub_type:
                        cache_secret_info = self.cache_map.get(secret_name)
                        if judge_secret_expired(secret_info.rotation_interval,
                                                cache_secret_info.refresh_time_stamp):
                            try:
                                finished = self.secret_cache_client.refresh_now(secret_name)
                                if not finished:
                                    monitor_message_utils.add_message(self.queue,
                                                                      MonitorMessageInfo(
                                                                          consts.MONITOR_AK_STATUS_ACTION,
                                                                          secret_name,
                                                                          None,
                                                                          "secret[%s] ak expire and fail to refresh" %
                                                                          secret_name), True)
                                else:
                                    monitor_message_utils.add_message(self.queue,
                                                                      MonitorMessageInfo(
                                                                          consts.MONITOR_AK_STATUS_ACTION,
                                                                          secret_name,
                                                                          None,
                                                                          "secret[%s] ak expire,but success to refresh" %
                                                                          secret_name))
                            except Exception as e:
                                monitor_message_utils.add_message(self.queue,
                                                                  MonitorMessageInfo(consts.MONITOR_AK_STATUS_ACTION,
                                                                                     secret_name,
                                                                                     None,
                                                                                     "secret[%s] ak expire and refresh with err[%s]" %
                                                                                     (secret_name, str(e)), True))
                    else:
                        raise ValueError("secret[%s] ExtendedConfig is invalid" % secret_name)
                else:
                    raise ValueError("secret[%s] ExtendedConfig is invalid" % secret_name)

        def consume_message(self):
            while not self.queue.empty():
                try:
                    monitor_message_info = self.queue.get(True)
                    common_logger.get_logger().warn(
                        "secretsmanager plugins monitor occur some problems secretName:%s,action:%s,errorMessage:%s,timestamp:%s " %
                        (monitor_message_info.secret_name, monitor_message_info.action,
                         monitor_message_info.error_message, monitor_message_info.timestamp))
                except Exception as e:
                    monitor_message_utils.add_message(self.queue,
                                                      MonitorMessageInfo(consts.CUSTOM_MESSAGE_ACTION,
                                                                         None,
                                                                         None,
                                                                         str(e), True))

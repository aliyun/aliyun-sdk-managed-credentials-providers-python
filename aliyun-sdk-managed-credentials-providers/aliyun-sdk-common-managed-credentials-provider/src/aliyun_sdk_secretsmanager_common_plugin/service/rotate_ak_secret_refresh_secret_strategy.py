# coding=utf-8
import json
import random
import time

from alibaba_cloud_secretsmanager_client.service.refresh_secret_strategy import RefreshSecretStrategy

from aliyun_sdk_secretsmanager_common_plugin.utils import consts, date_utils


def parse_next_rotation_time(secret_info):
    next_rotation_date = secret_info.next_rotation_date
    if next_rotation_date is None or next_rotation_date == "":
        secret_value_dict = json.loads(secret_info.secret_value)
        if secret_value_dict.get(consts.PROPERTY_NAME_KEY_SCHEDULE_ROTATE_TIMESTAMP) is None:
            return -1
        return secret_value_dict.get(consts.PROPERTY_NAME_KEY_SCHEDULE_ROTATE_TIMESTAMP) * 1000
    return date_utils.parse_date(next_rotation_date, date_utils.TIMEZONE_DATE_PATTERN) * 1000


class RotateAKSecretRefreshSecretStrategy(RefreshSecretStrategy):

    def __init__(self, rotation_interval=consts.DEFAULT_ROTATION_INTERVAL_IN_MS,
                 delay_interval=consts.DEFAULT_DELAY_INTERVAL):
        self.rotation_interval = rotation_interval
        self.delay_interval = delay_interval
        self.random_disturbance = random.randint(0, consts.DEFAULT_RANDOM_DISTURBANCE_RANGE)

    def init(self):
        pass

    def get_next_execute_time(self, secret_name, ttl, offset):
        now = int(round(time.time() * 1000))
        if ttl + offset > now:
            return ttl + offset + self.random_disturbance
        else:
            return now + ttl + self.random_disturbance

    def parse_next_execute_time(self, cache_secret_info):
        secret_info = cache_secret_info.secret_info
        next_rotation_date = parse_next_rotation_time(secret_info)
        now = int(round(time.time() * 1000))
        if next_rotation_date >= now + self.rotation_interval + self.random_disturbance or next_rotation_date <= now:
            return now + self.rotation_interval + self.random_disturbance
        else:
            return next_rotation_date + self.delay_interval + self.random_disturbance

    def parse_ttl(self, secret_info):
        if (secret_info.secret_type is not None and secret_info.secret_type != "") and \
                consts.RAM_CREDENTIALS_SECRET_TYPE == secret_info.secret_type:
            extended_config = secret_info.extended_config
            if extended_config is not None:
                extended_config_dict = json.loads(extended_config)
                secret_sub_type = extended_config_dict.get(consts.EXTENDED_CONFIG_PROPERTY_SECRET_SUB_TYPE, "")
                if consts.RAM_USER_ACCESS_KEY_SECRET_SUB_TYPE == secret_sub_type:
                    rotation_interval = secret_info.rotation_interval
                    if rotation_interval is None or rotation_interval == "":
                        return self.rotation_interval + self.random_disturbance
                    return int(rotation_interval.replace("s", "")) * 1000 + self.random_disturbance
        secret_value_dict = json.loads(secret_info.secret_value)
        refresh_interval = secret_value_dict.get(consts.PROPERTY_NAME_KEY_REFRESH_INTERVAL)
        if refresh_interval is None or refresh_interval == "":
            return -1
        return int(refresh_interval.replace("s", "")) * 1000 + self.random_disturbance

    def close(self):
        pass

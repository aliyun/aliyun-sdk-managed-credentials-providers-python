# coding=utf-8
import json
import sys
import time
import uuid

from alibaba_cloud_secretsmanager_client.model.secret_info import SecretInfo
from alibaba_cloud_secretsmanager_client.utils import const

from aliyun_sdk_secretsmanager_common_plugin.auth.secretsmanager_plugin_credentials import \
    SecretsManagerPluginCredentials
from aliyun_sdk_secretsmanager_common_plugin.utils import consts, date_utils


def generate_credentials_by_secret(secret_data):
    if secret_data is not None and secret_data != "":
        access_key_info = json.loads(secret_data)
        if consts.PROPERTY_NAME_KEY_ACCESS_KEY_ID in access_key_info.keys() and \
                consts.PROPERTY_NAME_KEY_ACCESS_KEY_SECRET in access_key_info.keys():
            access_key_id = access_key_info.get(consts.PROPERTY_NAME_KEY_ACCESS_KEY_ID)
            access_key_secret = access_key_info.get(consts.PROPERTY_NAME_KEY_ACCESS_KEY_SECRET)
        else:
            raise ValueError(str.format("illegal secret data[%s]", secret_data))
        expire_timestamp = consts.NOT_SUPPORT_TAMP_AK_TIMESTAMP
        if consts.PROPERTY_NAME_KEY_EXPIRE_TIMESTAMP in access_key_info.keys():
            expire_timestamp = date_utils.parse_date(access_key_info.get(consts.PROPERTY_NAME_KEY_EXPIRE_TIMESTAMP),
                                                     date_utils.TIMEZONE_DATE_PATTERN) * 1000
        generate_timestamp = sys.maxsize
        if consts.PROPERTY_NAME_KEY_GENERATE_TIMESTAMP in access_key_info.keys():
            generate_timestamp = date_utils.parse_date(access_key_info.get(consts.PROPERTY_NAME_KEY_GENERATE_TIMESTAMP),
                                                       date_utils.TIMEZONE_DATE_PATTERN) * 1000
        return SecretsManagerPluginCredentials(access_key_id, access_key_secret, expire_timestamp, generate_timestamp)
    else:
        raise ValueError("missing param secret data")


def generate_secret_info_by_credentials(secretsmanager_credentials, secret_name):
    if secretsmanager_credentials is not None:
        access_key_info = {consts.PROPERTY_NAME_KEY_ACCESS_KEY_ID: secretsmanager_credentials.access_key_id,
                           consts.PROPERTY_NAME_KEY_ACCESS_KEY_SECRET: secretsmanager_credentials.access_key_secret}
        secret_value = json.dumps(access_key_info)
        version_id = uuid.uuid4()
        create_time = date_utils.format_date(time.time(), date_utils.TIMEZONE_DATE_PATTERN)
        next_rotation_date = date_utils.format_date(time.time() + 24 * 60 * 60, date_utils.TIMEZONE_DATE_PATTERN)
        return SecretInfo(secret_name, version_id, secret_value, const.TEXT_DATA_TYPE, create_time,
                          consts.RAM_CREDENTIALS_SECRET_TYPE, consts.DEFAULT_AUTOMATIC_ROTATION, "",
                          consts.DEFAULT_ROTATION_INTERVAL, next_rotation_date)
    else:
        raise ValueError("missing param secretsmanager credentials")

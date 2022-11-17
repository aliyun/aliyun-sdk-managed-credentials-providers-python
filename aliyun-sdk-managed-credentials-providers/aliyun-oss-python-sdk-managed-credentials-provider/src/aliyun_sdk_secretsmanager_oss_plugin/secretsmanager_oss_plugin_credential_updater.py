# coding=utf-8
from aliyun_sdk_secretsmanager_common_plugin.secretsmanager_plugin_credential_updater import \
    SecretsMangerPluginCredentialUpdater

from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils


class SecretsMangerOssPluginCredentialUpdater(SecretsMangerPluginCredentialUpdater):

    def __init__(self, bucket, plugins_auth):
        self.__bucket = bucket
        self.__plugin_auth = plugins_auth

    def get_client(self):
        return self.__bucket

    def update_credential(self, secret_info):
        credentials = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
        self.__plugin_auth.switch_credentials(credentials.access_key_id, credentials.access_key_secret)

    def close(self):
        pass

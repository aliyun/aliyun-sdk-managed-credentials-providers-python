# coding=utf-8
import threading

from aliyun_sdk_secretsmanager_common_plugin.aliyun_sdk_secretsmanager_plugins_manager import \
    AliyunSdkSecretsManagerPluginsManager

from aliyun_sdk_secretsmanager_common_plugin.secretsmanager_plugin_builder import SecretsMangerPluginBuilder
from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils
from oss2 import Bucket

from aliyun_sdk_secretsmanager_oss_plugin.secretsmanager_oss_plugin_credential_updater import \
    SecretsMangerOssPluginCredentialUpdater
from aliyun_sdk_secretsmanager_oss_plugin.secretsmanger_plugin_auth import SecretsMangerPluginAuth

plugins_credential_updater_set = set([SecretsMangerOssPluginCredentialUpdater.__name__])


class SecretsManagerOssPluginManager(object):
    __secretsmanager_oss_plugin = None
    __lock = threading.RLock()

    @classmethod
    def get_bucket(cls, endpoint, bucket_name, secret_name, is_cname=False, session=None, connect_timeout=None,
                   app_name='',
                   enable_crc=True, bucket=None):
        cls.__init_secretsmanager_oss_plugin()
        return cls.__secretsmanager_oss_plugin._SecretsManagerOssPlugin__get_bucket(endpoint,
                                                                                    bucket_name, secret_name, is_cname,
                                                                                    session,
                                                                                    connect_timeout, app_name,
                                                                                    enable_crc, bucket)

    @classmethod
    def __init_secretsmanager_oss_plugin(cls):
        if cls.__secretsmanager_oss_plugin is None:
            with cls.__lock:
                if cls.__secretsmanager_oss_plugin is None:
                    AliyunSdkSecretsManagerPluginsManager.init()
                    cls.__secretsmanager_oss_plugin = SecretsManagerOssPluginManager.__SecretsManagerOssPlugin()

    @classmethod
    def close_client(cls, client, secret_name):
        cls.__secretsmanager_oss_plugin._SecretsManagerOssPlugin__close_client(client, secret_name)

    @classmethod
    def destroy(cls):
        cls.__secretsmanager_oss_plugin._SecretsManagerOssPlugin__destroy()

    class __SecretsManagerOssPlugin(object):

        def __get_bucket(self, endpoint, bucket_name, secret_name, is_cname=False, session=None, connect_timeout=None,
                         app_name='',
                         enable_crc=True, bucket=None):
            secret_info = AliyunSdkSecretsManagerPluginsManager.get_secret_info(secret_name)
            credentials = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
            plugins_auth = SecretsMangerPluginAuth(credentials.access_key_id, credentials.access_key_secret)
            if bucket is not None:
                bucket.auth = plugins_auth
            else:
                bucket_plugin_builder = self.__BucketSecretsMangerPluginBuilder(plugins_auth, endpoint,
                                                                                bucket_name,
                                                                                is_cname, session,
                                                                                connect_timeout, app_name,
                                                                                enable_crc)
                bucket = bucket_plugin_builder.build()
            updater = SecretsMangerOssPluginCredentialUpdater(bucket, plugins_auth)
            AliyunSdkSecretsManagerPluginsManager.register_secretsmanager_plugin_updater(secret_info.secret_name,
                                                                                         updater)
            return bucket

        def __close_client(self, client, secret_name):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client(secret_name, client)

        def __destroy(self):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client_by_updater(
                plugins_credential_updater_set)

        def __del__(self):
            self.__destroy()

        class __BucketSecretsMangerPluginBuilder(SecretsMangerPluginBuilder):

            def __init__(self, plugins_auth, endpoint, bucket_name, is_cname=False, session=None,
                         connect_timeout=None, app_name='', enable_crc=True):
                self.plugins_auth = plugins_auth
                self.endpoint = endpoint
                self.bucket_name = bucket_name
                self.is_cname = is_cname
                self.session = session
                self.connect_timeout = connect_timeout
                self.app_name = app_name
                self.enable_crc = enable_crc

            def build(self):
                return Bucket(self.plugins_auth, self.endpoint,
                              self.bucket_name, self.is_cname, self.session,
                              self.connect_timeout, self.app_name, self.enable_crc)

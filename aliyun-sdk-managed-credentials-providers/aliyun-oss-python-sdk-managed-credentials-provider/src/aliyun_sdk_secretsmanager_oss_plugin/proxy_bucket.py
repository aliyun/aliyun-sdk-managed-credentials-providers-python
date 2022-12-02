# coding=utf-8
from aliyun_sdk_secretsmanager_common_plugin.aliyun_sdk_secretsmanager_plugins_manager import \
    AliyunSdkSecretsManagerPluginsManager
from oss2 import Bucket
import oss2
from aliyun_sdk_secretsmanager_oss_plugin.oss_ak_expire_handler import OssAkExpireHandler
from aliyun_sdk_secretsmanager_oss_plugin.secretsmanager_oss_plugin_manager import SecretsManagerOssPluginManager


class ProxyBucket(Bucket):

    def __init__(self, secret_name, endpoint, bucket_name, is_cname=False, session=None, connect_timeout=None,
                 app_name='',
                 enable_crc=True, proxies=None, region=None, cloudbox_id=None, ak_expire_handler=None):
        self._secret_name = secret_name
        if ak_expire_handler is None:
            ak_expire_handler = OssAkExpireHandler()
        self._ak_expire_handler = ak_expire_handler
        super(ProxyBucket, self).__init__(secret_name, endpoint, bucket_name, is_cname, session, connect_timeout,
                                          app_name, enable_crc,
                                          proxies,
                                          region, cloudbox_id)
        self._init(secret_name, endpoint, bucket_name, is_cname, session, connect_timeout, app_name, enable_crc)

    def _init(self, secret_name, endpoint, bucket_name, is_cname=False, session=None, connect_timeout=None,
              app_name='',
              enable_crc=True):
        SecretsManagerOssPluginManager.get_bucket(endpoint, bucket_name, secret_name, is_cname,
                                                  session,
                                                  connect_timeout, app_name,
                                                  enable_crc, self)

    def _do(self, method, bucket_name, key, **kwargs):
        try:
            return super(ProxyBucket, self)._do(method, bucket_name, key, **kwargs)
        except oss2.exceptions.ServerError as e:
            if self._ak_expire_handler.judge_ak_expire(e):
                AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self._secret_name)
                return super(ProxyBucket, self)._do(method, bucket_name, key, **kwargs)
            else:
                raise e

    def shutdown(self):
        SecretsManagerOssPluginManager.close_client(self, self._secret_name)

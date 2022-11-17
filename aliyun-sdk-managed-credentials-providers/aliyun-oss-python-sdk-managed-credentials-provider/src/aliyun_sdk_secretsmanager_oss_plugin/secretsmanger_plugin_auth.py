# coding=utf-8
from alibaba_cloud_secretsmanager_client.utils import common_logger
from aliyun_sdk_secretsmanager_common_plugin.utils.read_write_lock import RWLock
from oss2 import Auth


class SecretsMangerPluginAuth(Auth):
    def __init__(self, access_key_id, access_key_secret):
        super(SecretsMangerPluginAuth, self).__init__(access_key_id, access_key_secret)
        self.rw_lock = RWLock()

    def switch_credentials(self, access_key_id, access_key_secret):
        if hasattr(self, "id") and hasattr(self, "secret"):
            try:
                lock = self.rw_lock.write_acquire(False)
                if not lock:
                    common_logger.get_logger().error("oss switch_credentials try lock fail")
                self.id = access_key_id
                self.secret = access_key_secret
            finally:
                if lock:
                    self.rw_lock.write_release()
        else:
            from oss2 import StaticCredentialsProvider
            self.credentials_provider = StaticCredentialsProvider(access_key_id,
                                                                  access_key_secret)

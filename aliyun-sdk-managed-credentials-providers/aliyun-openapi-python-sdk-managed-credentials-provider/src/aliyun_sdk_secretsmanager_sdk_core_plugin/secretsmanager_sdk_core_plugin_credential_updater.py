# coding=utf-8
from alibaba_cloud_secretsmanager_client.utils import common_logger
from aliyun_sdk_secretsmanager_common_plugin.secretsmanager_plugin_credential_updater import \
    SecretsMangerPluginCredentialUpdater
from aliyunsdkcore.auth import credentials
from aliyunsdkcore.auth.signers import access_key_signer

from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils


class SecretsMangerSdkCorePluginCredentialUpdater(SecretsMangerPluginCredentialUpdater):

    def __init__(self, client):
        self.__client = client

    def get_client(self):
        return self.__client

    def update_credential(self, secret_info):
        try:
            lock = self.__client.rw_lock.write_acquire(False)
            if not lock:
                common_logger.get_logger().error("sdk core update_credential try lock fail")
            credential = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
            self.__client._ak = credential.access_key_id
            self.__client._sk = credential.access_key_secret
            self.__client._signer = access_key_signer.AccessKeySigner(
                credentials.AccessKeyCredential(credential.access_key_id, credential.access_key_secret))
        finally:
            if lock:
                self.__client.rw_lock.write_release()

    def close(self):
        self.__client.__del__()

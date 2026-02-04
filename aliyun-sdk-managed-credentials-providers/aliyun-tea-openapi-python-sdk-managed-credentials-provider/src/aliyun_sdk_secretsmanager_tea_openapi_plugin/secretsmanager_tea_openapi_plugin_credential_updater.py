# coding=utf-8
from alibabacloud_credentials.utils import auth_constant
from aliyun_sdk_secretsmanager_common_plugin.secretsmanager_plugin_credential_updater import \
    SecretsMangerPluginCredentialUpdater
from alibabacloud_credentials import models as credential_models
from alibabacloud_credentials.client import Client as CredentialClient
from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils


class SecretsManagerTeaOpenApiPluginCredentialUpdater(SecretsMangerPluginCredentialUpdater):
    def __init__(self, open_api_client):
        self.open_api_client = open_api_client

    def get_client(self):
        return self.open_api_client

    def update_credential(self, secret_info):
        credentials = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
        credential_config = credential_models.Config(
            access_key_id=credentials.access_key_id,
            type=auth_constant.ACCESS_KEY,
            access_key_secret=credentials.access_key_secret
        )
        self.open_api_client._credential = CredentialClient(credential_config)

    def close(self):
        # do nothing
        pass

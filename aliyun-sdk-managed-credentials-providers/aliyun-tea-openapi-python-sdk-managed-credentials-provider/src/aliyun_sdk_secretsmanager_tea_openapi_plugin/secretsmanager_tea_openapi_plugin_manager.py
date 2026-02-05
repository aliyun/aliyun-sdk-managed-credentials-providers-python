# coding=utf-8
import threading
from typing import Type

from Tea.exceptions import TeaException
from alibabacloud_credentials.utils import auth_constant
from aliyun_sdk_secretsmanager_common_plugin.ak_expire_handler import AKExpireHandler
from aliyun_sdk_secretsmanager_common_plugin.aliyun_sdk_secretsmanager_plugins_manager import \
    AliyunSdkSecretsManagerPluginsManager
from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils
from alibabacloud_tea_openapi import models as open_api_models
from aliyun_sdk_secretsmanager_tea_openapi_plugin.secretsmanager_tea_openapi_plugin_credential_updater import \
    SecretsManagerTeaOpenApiPluginCredentialUpdater
from aliyun_sdk_secretsmanager_tea_openapi_plugin.tea_openapi_ak_expire_handler import \
    TeaOpenApiPluginAKExpireHandler
from alibabacloud_credentials import models as credential_models
from alibabacloud_credentials.client import Client as CredentialClient


class SecretsManagerTeaOpenApiPluginManager(object):
    __ak_expire_handler = None
    __secretsmanager_tea_openapi_plugin = None
    __lock = threading.RLock()
    _plugins_credential_updater_set = {SecretsManagerTeaOpenApiPluginCredentialUpdater.__name__}

    @classmethod
    def __init_secretsmanager_plugin(cls):
        if cls.__secretsmanager_tea_openapi_plugin is None:
            with cls.__lock:
                if cls.__secretsmanager_tea_openapi_plugin is None:
                    AliyunSdkSecretsManagerPluginsManager.init()
                    cls.__secretsmanager_tea_openapi_plugin = SecretsManagerTeaOpenApiPluginManager._SecretsManagerTeaOpenApiPlugin()
                    if cls.__ak_expire_handler is not None:
                        cls.__secretsmanager_tea_openapi_plugin.ak_expire_handler = cls.__ak_expire_handler

    @classmethod
    def get_tea_open_api_client(cls, endpoint: str, client_type: Type, secret_name: str,
                                ak_expire_handler: TeaOpenApiPluginAKExpireHandler):
        cls.__init_secretsmanager_plugin()
        return cls.__secretsmanager_tea_openapi_plugin._SecretsManagerTeaOpenApiPlugin__get_tea_open_api_client(
            endpoint, client_type, secret_name, ak_expire_handler)

    @classmethod
    def get_tea_open_api_client_with_config(cls, config: open_api_models.Config, client_type: Type, secret_name: str,
                                            ak_expire_handler: TeaOpenApiPluginAKExpireHandler):
        cls.__init_secretsmanager_plugin()
        return cls.__secretsmanager_tea_openapi_plugin._SecretsManagerTeaOpenApiPlugin__get_tea_open_api_client_with_config(
            config, client_type, secret_name, ak_expire_handler)

    @classmethod
    def close_client(cls, client, secret_name: str):
        cls.__secretsmanager_tea_openapi_plugin._SecretsManagerTeaOpenApiPlugin__close_client(client, secret_name)

    @classmethod
    def destroy(cls):
        cls.__secretsmanager_tea_openapi_plugin._SecretsManagerTeaOpenApiPlugin__destroy()

    class _SecretsManagerTeaOpenApiPlugin(object):

        def __init__(self):
            self.ak_expire_handler = TeaOpenApiPluginAKExpireHandler()

        def __get_tea_open_api_client(self, endpoint, client_type: Type, secret_name, ak_expire_handler):
            config = open_api_models.Config(endpoint=endpoint)
            return self.__get_tea_open_api_client_with_config(config, client_type, secret_name, ak_expire_handler)

        def __get_tea_open_api_client_with_config(self, config: open_api_models.Config, client_type: Type,
                                                  secret_name: str, ak_expire_handler):
            secret_info = AliyunSdkSecretsManagerPluginsManager.get_secret_info(secret_name)
            credentials = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
            tea_open_api_client_builder = SecretsManagerTeaOpenApiPluginManager._TeaOpenApiClientBuilder(config,
                                                                                                         credentials,
                                                                                                         client_type,
                                                                                                         secret_name,
                                                                                                         ak_expire_handler)
            tea_open_api_client = tea_open_api_client_builder.build()
            updater = SecretsManagerTeaOpenApiPluginCredentialUpdater(tea_open_api_client)
            AliyunSdkSecretsManagerPluginsManager.register_secretsmanager_plugin_updater(secret_info.secret_name,
                                                                                         updater)
            return tea_open_api_client

        def __close_client(self, client, secret_name):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client(secret_name, client)

        def __destroy(self):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client_by_updater(
                SecretsManagerTeaOpenApiPluginManager._plugins_credential_updater_set)

    class _TeaOpenApiClientBuilder:
        def __init__(self, config: open_api_models.Config, credentials, client_type: Type, secret_name: str,
                     ak_expire_handler: AKExpireHandler):
            self.credentials = credentials
            self.client_type = client_type
            self.config = config
            self.secret_name = secret_name
            self.ak_expire_handler = ak_expire_handler

        def build(self):
            credential_config = credential_models.Config(
                access_key_id=self.credentials.access_key_id,
                type=auth_constant.ACCESS_KEY,
                access_key_secret=self.credentials.access_key_secret
            )
            self.config.credential = CredentialClient(credential_config)
            return self.generate_proxy_client(self.client_type)

        def generate_proxy_client(self, client_type: Type):
            class TeaOpenApiProxyClient(client_type):
                def __init__(self, config: open_api_models.Config, ak_expire_handler: AKExpireHandler, secret_name):
                    super().__init__(config)
                    self.ak_expire_handler = ak_expire_handler
                    self.secret_name = secret_name

                def do_request(self, *args, **kwargs):
                    try:
                        return super().do_request(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return super().do_request(*args, **kwargs)
                        raise e

                async def do_request_async(self, *args, **kwargs):
                    try:
                        return await super().do_request_async(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return await super().do_request_async(*args, **kwargs)
                        raise e

                def do_roarequest(self, *args, **kwargs):
                    try:
                        return super().do_roarequest(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return super().do_roarequest(*args, **kwargs)
                        raise e

                async def do_roarequest_async(self, *args, **kwargs):
                    try:
                        return await super().do_roarequest_async(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return await super().do_roarequest_async(*args, **kwargs)
                        raise e

                def do_roarequest_with_form(self, *args, **kwargs):
                    try:
                        return super().do_roarequest_with_form(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return super().do_roarequest_with_form(*args, **kwargs)
                        raise e

                async def do_roarequest_with_form_async(self, *args, **kwargs):
                    try:
                        return await super().do_roarequest_with_form_async(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return await super().do_roarequest_with_form_async(*args, **kwargs)
                        raise e

                def do_rpcrequest(self, *args, **kwargs):
                    try:
                        return super().do_rpcrequest(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return super().do_rpcrequest(*args, **kwargs)
                        raise e

                async def do_rpcrequest_async(self, *args, **kwargs):
                    try:
                        return await super().do_rpcrequest_async(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return await super().do_rpcrequest_async(*args, **kwargs)
                        raise e

                def execute(self, *args, **kwargs):
                    try:
                        return super().execute(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return super().execute(*args, **kwargs)
                        raise e

                async def execute_async(self, *args, **kwargs):
                    try:
                        return await super().execute_async(*args, **kwargs)
                    except TeaException as e:
                        if self.ak_expire_handler.judge_ak_expire(e):
                            AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                            return await super().execute_async(*args, **kwargs)
                        raise e

            return TeaOpenApiProxyClient(self.config, self.ak_expire_handler, self.secret_name)

# coding=utf-8
from typing import Type

from aliyun_sdk_secretsmanager_tea_openapi_plugin.secretsmanager_tea_openapi_plugin_manager import \
    SecretsManagerTeaOpenApiPluginManager
from aliyun_sdk_secretsmanager_tea_openapi_plugin.tea_openapi_ak_expire_handler import TeaOpenApiPluginAKExpireHandler
from alibabacloud_tea_openapi import models as open_api_models


def create_client(endpoint: str, client_type: Type, secret_name: str,
                  ak_expire_handler=TeaOpenApiPluginAKExpireHandler()):
    return SecretsManagerTeaOpenApiPluginManager.get_tea_open_api_client(endpoint, client_type, secret_name,
                                                                         ak_expire_handler)


def create_client_with_config(config: open_api_models.Config, client_type: Type, secret_name: str,
                              ak_expire_handler=TeaOpenApiPluginAKExpireHandler()):
    return SecretsManagerTeaOpenApiPluginManager.get_tea_open_api_client_with_config(config, client_type,
                                                                                     secret_name, ak_expire_handler)

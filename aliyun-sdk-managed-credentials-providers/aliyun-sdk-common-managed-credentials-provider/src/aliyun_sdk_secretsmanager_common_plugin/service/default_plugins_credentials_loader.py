# coding=utf-8
import sys

from aliyun_sdk_secretsmanager_common_plugin.model.secretsmanager_plugin_credentials_provider import \
    SecretsManagerPluginCredentialsProvider
from aliyun_sdk_secretsmanager_common_plugin.service.default_secretsmanager_plugin_cache_hook import \
    DefaultSecretsManagerPluginCacheHook
from aliyun_sdk_secretsmanager_common_plugin.service.monitor_memory_cache_secret_store_strategy import \
    MonitorMemoryCacheSecretStoreStrategy
from aliyun_sdk_secretsmanager_common_plugin.service.secretsmanager_plugin_credentials_loader import \
    SecretsManagerPluginCredentialsLoader
from aliyun_sdk_secretsmanager_common_plugin.service.rotate_ak_secret_refresh_secret_strategy import \
    RotateAKSecretRefreshSecretStrategy
from aliyun_sdk_secretsmanager_common_plugin.service.secret_exchange import SecretExchange
from aliyun_sdk_secretsmanager_common_plugin.service.secret_recovery_strategy import SecretRecoveryStrategy
from aliyun_sdk_secretsmanager_common_plugin.utils import consts

if sys.version_info.major == 2:
    from Queue import Queue
else:
    from queue import Queue

from alibaba_cloud_secretsmanager_client.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy
from alibaba_cloud_secretsmanager_client.utils import credentials_properties_utils


class DefaultPluginCredentialsLoader(SecretsManagerPluginCredentialsLoader):

    def load(self):
        credential_properties = credentials_properties_utils.load_credentials_properties(
            consts.DEFAULT_CREDENTIALS_CONFIG_NAME)
        if credential_properties is not None:
            monitor_period_milliseconds = credential_properties.source_properties.get(
                consts.PROPERTIES_MONITOR_PERIOD_MILLISECONDS_KEY)
            monitor_customer_milliseconds = credential_properties.source_properties.get(
                consts.PROPERTIES_MONITOR_CUSTOMER_MILLISECONDS_KEY)
            queue = Queue(1000)
            return SecretsManagerPluginCredentialsProvider(credential_properties.credential,
                                                           credential_properties.region_info_list,
                                                           credential_properties.secret_name_list,
                                                           SecretExchange(),
                                                           MonitorMemoryCacheSecretStoreStrategy(queue,
                                                                                                 monitor_period_milliseconds,
                                                                                                 monitor_customer_milliseconds),
                                                           DefaultSecretsManagerPluginCacheHook(queue,
                                                                                                SecretRecoveryStrategy()),
                                                           FullJitterBackoffStrategy(consts.RETRY_MAX_ATTEMPTS,
                                                                                     consts.RETRY_INITIAL_INTERVAL_MILLS,
                                                                                     consts.CAPACITY),
                                                           RotateAKSecretRefreshSecretStrategy(),
                                                           credential_properties.dkms_configs_dict)
        else:
            raise ValueError("missing default config [%s]" % consts.DEFAULT_CREDENTIALS_CONFIG_NAME)

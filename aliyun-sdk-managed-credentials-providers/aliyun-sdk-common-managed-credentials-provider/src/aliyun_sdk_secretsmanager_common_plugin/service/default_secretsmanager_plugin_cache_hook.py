# coding=utf-8
import time

from alibaba_cloud_secretsmanager_client.model.secret_info import CacheSecretInfo

from aliyun_sdk_secretsmanager_common_plugin.model.monitor_message_info import MonitorMessageInfo
from aliyun_sdk_secretsmanager_common_plugin.service.secretsmanager_plugin_cache_hook import \
    SecretsManagerPluginCacheHook
from aliyun_sdk_secretsmanager_common_plugin.utils import monitor_message_utils, consts


class DefaultSecretsManagerPluginCacheHook(SecretsManagerPluginCacheHook):

    def __init__(self, queue, secret_recover_strategy):
        super(DefaultSecretsManagerPluginCacheHook, self).__init__()
        self.queue = queue
        self.secret_recover_strategy = secret_recover_strategy

    def init(self):
        pass

    def put(self, secret_info):
        secret_name = secret_info.secret_name
        updater_list = self.plugins_updater_dict.get(secret_name)
        if updater_list is not None:
            for updater in updater_list:
                try:
                    updater.update_credential(secret_info)
                except Exception as e:
                    monitor_message_utils.add_message(self.queue,
                                                      MonitorMessageInfo(consts.UPDATE_CREDENTIAL_ACTION,
                                                                         secret_name,
                                                                         None, str(e),
                                                                         True))
        return CacheSecretInfo(consts.KMS_SECRET_CURRENT_STAGE_VERSION, int(round(time.time() * 1000)), secret_info)

    def get(self, cache_secret_info):
        return cache_secret_info.secret_info

    def recovery_get_secret(self, secret_name):
        secret_info = self.secret_recover_strategy.recover_get_secret(secret_name)
        if secret_info is not None:
            monitor_message_utils.add_message(self.queue,
                                              MonitorMessageInfo(consts.RECOVERY_GET_SECRET_ACTION,
                                                                 secret_name,
                                                                 None,
                                                                 "The secret named [%s] recovery success" %
                                                                 secret_name,
                                                                 True))
            return secret_info
        monitor_message_utils.add_message(self.queue,
                                          MonitorMessageInfo(consts.RECOVERY_GET_SECRET_ACTION,
                                                             secret_name,
                                                             None,
                                                             "The secret named [%s] recovery fail" %
                                                             secret_name,
                                                             True))
        return None

    def close(self):
        if len(self.plugins_updater_dict) > 0:
            for updater_list in self.plugins_updater_dict.values():
                for updater in updater_list[:]:
                    updater.close()
                    updater_list.remove(updater)

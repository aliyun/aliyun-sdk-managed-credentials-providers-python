# coding=utf-8
import abc
import threading

from alibaba_cloud_secretsmanager_client.cache.secret_cache_hook import SecretCacheHook


class SecretsManagerPluginCacheHook(SecretCacheHook):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.plugins_updater_dict = {}
        self.lock = threading.RLock()

    def register_secretsmanager_plugin_updater(self, secret_name, plugins_updater):
        updater_list = self.plugins_updater_dict.get(secret_name)
        if updater_list is None:
            with self.lock:
                if updater_list is None:
                    self.plugins_updater_dict[secret_name] = []
            updater_list = self.plugins_updater_dict.get(secret_name)
        updater_list.append(plugins_updater)

    def close_secretsmanager_plugin_updater_and_client(self, secret_name, client):
        updater_list = self.plugins_updater_dict.get(secret_name)
        for updater in updater_list[:]:
            if updater.get_client() is client:
                updater_list.remove(updater)
                updater.close()
        return len(updater_list)

    def close_secretsmanager_plugin_updater_and_client_by_updater(self, updater_names):
        if len(self.plugins_updater_dict) > 0:
            for updater_list in self.plugins_updater_dict.values():
                for updater in updater_list[:]:
                    if type(updater).__name__ in updater_names:
                        updater.close()
                        updater_list.remove(updater)
        return len(self.plugins_updater_dict)

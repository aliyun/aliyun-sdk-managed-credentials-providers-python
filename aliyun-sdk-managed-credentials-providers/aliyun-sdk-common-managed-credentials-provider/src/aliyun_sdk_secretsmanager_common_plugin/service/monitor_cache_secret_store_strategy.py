# coding=utf-8
import abc

from alibaba_cloud_secretsmanager_client.cache.cache_secret_store_strategy import CacheSecretStoreStrategy


class MonitorCacheSecretStoreStrategy(CacheSecretStoreStrategy):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_refresh_hook(self, client):
        pass

# coding=utf-8
import abc


class SecretsMangerPluginCredentialUpdater(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_client(self):
        pass

    @abc.abstractmethod
    def update_credential(self, secret_info):
        pass

    @abc.abstractmethod
    def close(self):
        pass

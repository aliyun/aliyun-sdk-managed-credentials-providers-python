# coding=utf-8
import abc


class SecretsManagerPluginCredentialsLoader(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self):
        pass

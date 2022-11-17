# coding=utf-8
import abc


class SecretsMangerPluginBuilder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def build(self):
        pass

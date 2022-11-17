# coding=utf-8
import abc

from aliyun_sdk_secretsmanager_common_plugin.ak_expire_handler import AKExpireHandler


class DefaultAKExpireHandler(AKExpireHandler):
    __metaclass__ = abc.ABCMeta

    def judge_ak_expire(self, exception):
        if self.get_ak_expire_code() == self.get_error_code(exception):
            return True
        return False

    @abc.abstractmethod
    def get_error_code(self, exception):
        pass

    @abc.abstractmethod
    def get_ak_expire_code(self):
        pass

# coding=utf-8
import abc


class AKExpireHandler(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def judge_ak_expire(self, exception):
        """判断异常是否由Ak过期引起"""
        pass

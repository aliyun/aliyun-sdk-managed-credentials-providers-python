# coding=utf-8

class ConfigLoader(object):
    __config_name = None

    @staticmethod
    def get_config_name():
        return ConfigLoader.__config_name

    @staticmethod
    def set_config_name(config_name):
        ConfigLoader.__config_name = config_name

# coding=utf-8


class SecretsManagerPluginCredentialsProvider:

    def __init__(self, credentials=None,
                 region_info_list=None, secret_names=None, secret_exchange=None, cache_secret_store_strategy=None,
                 secretsmanager_plugin_cache_hook=None, back_off_strategy=None, refresh_secret_strategy=None,
                 dkms_configs_dict=None):
        self.credentials = credentials
        self.secret_exchange = secret_exchange
        self.region_info_list = region_info_list
        self.secret_names = secret_names
        self.cache_secret_store_strategy = cache_secret_store_strategy
        self.secretsmanager_plugin_cache_hook = secretsmanager_plugin_cache_hook
        self.back_off_strategy = back_off_strategy
        self.refresh_secret_strategy = refresh_secret_strategy
        self.dkms_configs_dict = dkms_configs_dict

# coding=utf-8
import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

from alibaba_cloud_secretsmanager_client.secret_manager_cache_client_builder import \
    SecretManagerCacheClientBuilder
from alibaba_cloud_secretsmanager_client.service.default_secret_manager_client_builder import \
    DefaultSecretManagerClientBuilder
from alibaba_cloud_secretsmanager_client.utils import const, common_logger

from aliyun_sdk_secretsmanager_common_plugin.service.default_plugins_credentials_loader import \
    DefaultPluginCredentialsLoader
from aliyun_sdk_secretsmanager_common_plugin.utils import consts, credentials_utils


class AliyunSdkSecretsManagerPluginsManager:
    __aliyun_sdk_secretsmanager_plugin = None
    __instance_lock = threading.Lock()
    __secretsmanager_plugin_credentials_loader = None

    @classmethod
    def init(cls, loader=None):
        if cls.__aliyun_sdk_secretsmanager_plugin is None:
            with cls.__instance_lock:
                if cls.__aliyun_sdk_secretsmanager_plugin is None:
                    cls.__aliyun_sdk_secretsmanager_plugin = cls.__AliyunSdkSecretsManagerPlugin(loader)
                    cls.__aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__init()

    @classmethod
    def get_access_key(cls, secret_name):
        return cls.get_aliyun_sdk_secretsmanager_plugin()._AliyunSdkSecretsManagerPlugin__get_access_key(secret_name)

    @classmethod
    def get_access_key_id(cls, secret_name):
        plugin_credentials = cls.get_access_key(secret_name)
        if plugin_credentials is None:
            raise ValueError("can not find access key id by the secret_name[%s]" % secret_name)
        return plugin_credentials.get_access_key_id()

    @classmethod
    def get_access_key_secret(cls, secret_name):
        plugins_credentials = cls.get_access_key(secret_name)
        if plugins_credentials is None:
            raise ValueError("can not find access key id by the secret_name[%s]" % secret_name)
        return plugins_credentials.get_access_key_secret()

    @classmethod
    def get_secret_info(cls, secret_name):
        return cls.get_aliyun_sdk_secretsmanager_plugin()._AliyunSdkSecretsManagerPlugin__get_secret_info(secret_name)

    @classmethod
    def refresh_secret_info(cls, secret_name):
        aliyun_sdk_secretsmanager_plugin = cls.get_aliyun_sdk_secretsmanager_plugin()
        return aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__refresh_secret_info(secret_name)

    @classmethod
    def get_aliyun_sdk_secretsmanager_plugin(cls):
        if cls.__aliyun_sdk_secretsmanager_plugin is None:
            raise RuntimeError("not initialize aliyun sdk secretsmanager plugin")
        return cls.__aliyun_sdk_secretsmanager_plugin

    @classmethod
    def get_secret_name(cls, secret_name):
        aliyun_sdk_secretsmanager_plugin = cls.get_aliyun_sdk_secretsmanager_plugin()
        return aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__get_secret_name(secret_name)

    @classmethod
    def register_secretsmanager_plugin_updater(cls, secret_name, plugins_updater):
        aliyun_sdk_secretsmanager_plugin = cls.get_aliyun_sdk_secretsmanager_plugin()
        return aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__register_secretsmanager_plugin_updater(
            secret_name,
            plugins_updater)

    @classmethod
    def close_secretsmanager_plugin_updater_and_client(cls, secret_name, client):
        aliyun_sdk_secretsmanager_plugin = cls.get_aliyun_sdk_secretsmanager_plugin()
        aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__close_secretsmanager_plugin_updater_and_client(
            secret_name,
            client)

    @classmethod
    def close_secretsmanager_plugin_updater_and_client_by_updater(cls, updater_names):
        aliyun_sdk_secretsmanager_plugin = cls.get_aliyun_sdk_secretsmanager_plugin()
        aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__close_secretsmanager_plugin_updater_and_client_by_updater(
            updater_names)

    @classmethod
    def shutdown(cls):
        if cls.__aliyun_sdk_secretsmanager_plugin is None:
            raise RuntimeError("Not initialize aliyun sdk secretsmanager plugin")
        cls.__aliyun_sdk_secretsmanager_plugin._AliyunSdkSecretsManagerPlugin__shutdown()

    class __AliyunSdkSecretsManagerPlugin(object):

        def __init__(self, loader):
            self.__secret_cache_client = None
            self.__refresh_timestamp_dict = {}
            self.__secretsmanager_plugin_credentials_loader = loader
            self.__secretsmanager_plugin_credentials_provider = None
            self.__lock = threading.Lock()

        def __init(self):
            self.__init_logger()
            if self.__secretsmanager_plugin_credentials_loader is not None:
                self.__secretsmanager_plugin_credentials_provider = self.__secretsmanager_plugin_credentials_loader.load()
                self.check_secretsmanager_plugin_credentials_provider()
            else:
                self.__secretsmanager_plugin_credentials_provider = DefaultPluginCredentialsLoader().load()
            self.__init_secret_manager_client()
            threading.Thread(target=self.__refresh_secrets).start()
            common_logger.get_logger().info("aliyunSdkSecretsManagerPlugin init success")

        def check_secretsmanager_plugin_credentials_provider(self):
            if self.__secretsmanager_plugin_credentials_provider.dkms_configs_dict is None and \
                    len(self.__secretsmanager_plugin_credentials_provider.dkms_configs_dict) == 0 \
                    and self.__secretsmanager_plugin_credentials_provider.credentials is None:
                raise ValueError(
                    "secretsmanager plugin credentials provider missing property[credentials] or property[cache_client_dkms_config_info]")
            if self.__secretsmanager_plugin_credentials_provider.secret_exchange is None:
                raise ValueError("secretsmanager plugin credentials provider missing property[secret_exchange]")
            if self.__secretsmanager_plugin_credentials_provider.cache_secret_store_strategy is None:
                raise ValueError(
                    "secretsmanager plugins credentials provider missing property[cache_secret_store_strategy]")
            if self.__secretsmanager_plugin_credentials_provider.secretsmanager_plugin_cache_hook is None:
                raise ValueError(
                    "secretsmanager plugins credentials provider missing property[secretsmanager_plugin_cache_hook]")
            if self.__secretsmanager_plugin_credentials_provider.back_off_strategy is None:
                raise ValueError("secretsmanager plugins credentials provider missing property[back_off_strategy]")

        @staticmethod
        def __init_logger():
            if common_logger.get_logger() is None:
                logger = logging.getLogger(const.DEFAULT_LOGGER_NAME)
                common_logger.set_logger(logger)
                logger.setLevel(level=logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s- %(module)s - %(levelname)s - %(message)s')
                log_file = "%s%s%s%s%s" % (
                    os.path.expanduser("~"), os.sep, "secretsmanager", os.sep, "secretsmanager_plugin.log")
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                file_handler = RotatingFileHandler(log_file, mode='a+', encoding="utf-8", maxBytes=50 * 1024 * 1024,
                                                   backupCount=5)
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

        def __refresh_secrets(self):
            for secret_name in self.__secretsmanager_plugin_credentials_provider.secret_names:
                try:
                    self.__refresh_secret_info(secret_name)
                except Exception:
                    common_logger.get_logger().error("action:refresh_secrets", exc_info=True)

        def __init_secret_manager_client(self):
            lock = self.__lock.acquire()
            try:
                client_builder = DefaultSecretManagerClientBuilder.standard()
                dkms_configs_dict = self.__secretsmanager_plugin_credentials_provider.dkms_configs_dict
                if dkms_configs_dict is not None and len(dkms_configs_dict) != 0:
                    for dkms_config in dkms_configs_dict.values():
                        client_builder.add_dkms_config(dkms_config)
                else:
                    if self.__secretsmanager_plugin_credentials_provider.credentials is not None:
                        client_builder = client_builder.with_credentials(
                            self.__secretsmanager_plugin_credentials_provider.credentials)
                client_builder = client_builder.with_back_off_strategy(
                    self.__secretsmanager_plugin_credentials_provider.back_off_strategy)
                if self.__secretsmanager_plugin_credentials_provider.region_info_list is not None:
                    for region_info in self.__secretsmanager_plugin_credentials_provider.region_info_list:
                        client_builder.add_region_info(region_info)
                self.__secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
                    client_builder.build()).with_cache_secret_strategy(
                    self.__secretsmanager_plugin_credentials_provider.cache_secret_store_strategy).with_refresh_secret_strategy(
                    self.__secretsmanager_plugin_credentials_provider.refresh_secret_strategy).with_secret_cache_hook(
                    self.__secretsmanager_plugin_credentials_provider.secretsmanager_plugin_cache_hook).build()
                self.__secretsmanager_plugin_credentials_provider.cache_secret_store_strategy.add_refresh_hook(
                    self.__secret_cache_client)
            finally:
                if lock:
                    self.__lock.release()

        def __judge_refresh_secret_info(self, secret_name):
            if secret_name in self.__refresh_timestamp_dict.keys():
                token_bucket = self.__refresh_timestamp_dict.get(secret_name)
                return token_bucket.has_quota()
            else:
                new_token_bucket = self.__TokenBucket(consts.DEFAULT_MAX_TOKEN_NUMBER, consts.DEFAULT_RATE_LIMIT_PERIOD)
                self.__refresh_timestamp_dict[secret_name] = new_token_bucket
                return new_token_bucket.has_quota()

        def __find_secret_name(self, secret_name):
            if secret_name is None or secret_name == "":
                raise ValueError("secret_name can not be null")
            secret_name = self.__secretsmanager_plugin_credentials_provider.secret_exchange.exchange_secret_name(
                secret_name)
            if secret_name is None or secret_name == "":
                raise ValueError("can not find secret name by the secret_name[%s]" % secret_name)
            return secret_name

        def __get_secret_name(self, secret_name):
            return self.__find_secret_name(secret_name)

        def __get_access_key(self, secret_name):
            secret_info = self.__get_secret_info(secret_name)
            return credentials_utils.generate_credentials_by_secret(secret_info.secret_value)

        def __get_secret_info(self, secret_name):
            secret_name = self.__find_secret_name(secret_name)
            return self.__secret_cache_client.get_secret_info(secret_name=secret_name)

        def __register_secretsmanager_plugin_updater(self, secret_name, plugins_updater):
            self.__secretsmanager_plugin_credentials_provider.secretsmanager_plugin_cache_hook.register_secretsmanager_plugin_updater(
                secret_name, plugins_updater)

        def __refresh_secret_info(self, secret_name):
            if self.__judge_refresh_secret_info(secret_name):
                self.__secret_cache_client.refresh_now(secret_name)
                time.sleep(0.2)

        def __close_secretsmanager_plugin_updater_and_client(self, secret_name, client):
            remain_updater_count = self.__secretsmanager_plugin_credentials_provider.secretsmanager_plugin_cache_hook.close_secretsmanager_plugin_updater_and_client(
                secret_name, client)
            if remain_updater_count == 0:
                self.__shutdown()

        def __close_secretsmanager_plugin_updater_and_client_by_updater(self, updater_names):
            remain_updater_count = self.__secretsmanager_plugin_credentials_provider.secretsmanager_plugin_cache_hook.close_secretsmanager_plugin_updater_and_client_by_updater(
                updater_names)
            if remain_updater_count == 0:
                self.__shutdown()

        def __shutdown(self):
            lock = self.__lock.acquire()
            try:
                if self.__secret_cache_client is not None:
                    self.__secret_cache_client.close()
            finally:
                if lock:
                    self.__lock.release()

        def __del__(self):
            self.__shutdown()

        class __TokenBucket(object):

            def __init__(self, max_tokens, rate):
                self.max_tokens = max_tokens
                self.current_tokens = max_tokens
                self.rate = rate
                self.last_update_time = int(round(time.time() * 1000))
                self.lock = threading.RLock()

            def has_quota(self):
                with self.lock:
                    now = int(round(time.time() * 1000))
                    new_tokens = int(round(now - self.last_update_time) * 1.0 / self.rate)
                    if new_tokens > 0:
                        self.last_update_time = now
                    self.current_tokens += new_tokens
                    if self.current_tokens > self.max_tokens:
                        self.current_tokens = self.max_tokens
                    remaining = self.current_tokens - 1
                    if remaining >= 0:
                        self.current_tokens = remaining
                        return True
                return False

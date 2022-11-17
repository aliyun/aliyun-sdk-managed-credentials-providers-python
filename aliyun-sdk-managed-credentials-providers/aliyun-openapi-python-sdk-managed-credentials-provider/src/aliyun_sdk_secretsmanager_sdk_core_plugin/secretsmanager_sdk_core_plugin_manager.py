# coding=utf-8
import threading

from alibaba_cloud_secretsmanager_client.utils import common_logger
from aliyunsdkcore.auth.signers.signer_factory import SignerFactory
from aliyunsdkcore.endpoint.default_endpoint_resolver import DefaultEndpointResolver

from aliyun_sdk_secretsmanager_common_plugin.secretsmanager_plugin_builder import SecretsMangerPluginBuilder
from aliyun_sdk_secretsmanager_common_plugin.aliyun_sdk_secretsmanager_plugins_manager import \
    AliyunSdkSecretsManagerPluginsManager
from aliyun_sdk_secretsmanager_common_plugin.utils import credentials_utils
from aliyun_sdk_secretsmanager_common_plugin.utils.read_write_lock import RWLock
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth import credentials
from aliyunsdkcore.client import AcsClient

from aliyun_sdk_secretsmanager_sdk_core_plugin.sdk_core_ak_expire_handler import SdkCoreAKExpireHandler
from aliyun_sdk_secretsmanager_sdk_core_plugin.secretsmanager_sdk_core_plugin_credential_updater import \
    SecretsMangerSdkCorePluginCredentialUpdater

plugins_credential_updater_set = set([SecretsMangerSdkCorePluginCredentialUpdater.__name__])


class SecretsManagerSdkCorePluginManager(object):
    __ak_expire_handler = None
    __secretsmanager_sdk_core_plugin = None
    __lock = threading.RLock()

    @classmethod
    def __init_secretsmanager_plugin(cls):
        if cls.__secretsmanager_sdk_core_plugin is None:
            with cls.__lock:
                if cls.__secretsmanager_sdk_core_plugin is None:
                    AliyunSdkSecretsManagerPluginsManager.init()
                    cls.__secretsmanager_sdk_core_plugin = SecretsManagerSdkCorePluginManager.__SecretsManagerSdkCorePlugin()
                    if cls.__ak_expire_handler is not None:
                        cls.__secretsmanager_sdk_core_plugin._SecretsManagerSdkCorePlugin__set_ak_expire_handler(
                            cls.__ak_expire_handler)

    @classmethod
    def get_acs_client(cls, secret_name, region_id="cn-hangzhou",
                       auto_retry=True,
                       max_retry_time=None,
                       user_agent=None,
                       port=80,
                       connect_timeout=None,
                       timeout=None,
                       public_key_id=None,
                       private_key=None,
                       session_period=3600,
                       debug=False,
                       verify=None, ak_expire_handler=None, default_client=None):
        cls.__init_secretsmanager_plugin()
        return cls.__secretsmanager_sdk_core_plugin._SecretsManagerSdkCorePlugin__get_acs_client(secret_name,
                                                                                                 region_id=region_id,
                                                                                                 auto_retry=auto_retry,
                                                                                                 max_retry_time=max_retry_time,
                                                                                                 user_agent=user_agent,
                                                                                                 port=port,
                                                                                                 connect_timeout=connect_timeout,
                                                                                                 timeout=timeout,
                                                                                                 public_key_id=public_key_id,
                                                                                                 private_key=private_key,
                                                                                                 session_period=session_period,
                                                                                                 debug=debug,
                                                                                                 verify=verify,
                                                                                                 ak_expire_handler=ak_expire_handler,
                                                                                                 default_client=default_client)

    @classmethod
    def set_ak_expire_handler(cls, ak_expire_handler):
        cls.__secretsmanager_sdk_core_plugin._SecretsManagerSdkCorePlugin__set_ak_expire_handler(
            ak_expire_handler)

    @classmethod
    def close_client(cls, client, secret_name):
        cls.__secretsmanager_sdk_core_plugin._SecretsManagerSdkCorePlugin__close_client(client, secret_name)

    @classmethod
    def destroy(cls):
        cls.__secretsmanager_sdk_core_plugin._SecretsManagerSdkCorePlugin__destroy()

    class __SecretsManagerSdkCorePlugin(object):

        def __init__(self):
            self.ak_expire_handler = None

        def __set_ak_expire_handler(self, ak_expire_handler):
            self.ak_expire_handler = ak_expire_handler

        def __get_acs_client(self, secret_name, region_id, auto_retry,
                             max_retry_time,
                             user_agent,
                             port,
                             connect_timeout,
                             timeout,
                             public_key_id,
                             private_key,
                             session_period,
                             debug,
                             verify, default_client=None, ak_expire_handler=None):
            secret_info = AliyunSdkSecretsManagerPluginsManager.get_secret_info(secret_name)
            credential = credentials_utils.generate_credentials_by_secret(secret_info.secret_value)
            ak_expire_handler = SdkCoreAKExpireHandler() if ak_expire_handler is None \
                else ak_expire_handler
            if default_client is not None:
                default_client._ak = credential.access_key_id
                default_client._secret = credential.access_key_secret
                credential = {
                    'ak': credential.access_key_id,
                    'secret': credential.access_key_secret,
                }
                default_client._signer = SignerFactory.get_signer(
                    credential, region_id, default_client._implementation_of_do_action, debug)
                client = default_client
            else:
                client = self.__AcsClientBuilder(secret_name, ak_expire_handler,
                                                 ak=credential.access_key_id,
                                                 secret=credential.access_key_secret,
                                                 region_id=region_id,
                                                 auto_retry=auto_retry,
                                                 max_retry_time=max_retry_time,
                                                 user_agent=user_agent,
                                                 port=port,
                                                 connect_timeout=connect_timeout,
                                                 timeout=timeout,
                                                 public_key_id=public_key_id,
                                                 private_key=private_key,
                                                 session_period=session_period,
                                                 credential=credentials.AccessKeyCredential(
                                                     credential.access_key_id,
                                                     credential.access_key_secret),
                                                 debug=debug,
                                                 verify=verify).build()
            plugins_credential_updater = SecretsMangerSdkCorePluginCredentialUpdater(client)
            AliyunSdkSecretsManagerPluginsManager.register_secretsmanager_plugin_updater(secret_name,
                                                                                         plugins_credential_updater)
            return client

        def __close_client(self, client, secret_name):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client(secret_name, client)

        def __del__(self):
            self.__destroy()

        def __destroy(self):
            AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client_by_updater(
                plugins_credential_updater_set)

        class __AcsClientBuilder(SecretsMangerPluginBuilder):

            def __init__(self, secret_name, ak_expire_handler, ak, secret,
                         region_id,
                         auto_retry,
                         max_retry_time,
                         user_agent,
                         port,
                         connect_timeout,
                         timeout,
                         public_key_id,
                         private_key,
                         session_period,
                         credential,
                         debug,
                         verify):
                self.secret_name = secret_name
                self.ak_expire_handler = ak_expire_handler
                self.ak = ak
                self.secret = secret
                self.region_id = region_id
                self.auto_retry = auto_retry
                self.max_retry_time = max_retry_time
                self.user_agent = user_agent
                self.port = port
                self.connect_timeout = connect_timeout
                self.timeout = timeout
                self.public_key_id = public_key_id
                self.private_key = private_key
                self.session_period = session_period
                self.credential = credential
                self.debug = debug
                self.verify = verify

            def build(self):
                return SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient(self.secret_name,
                                                                                    self.ak_expire_handler,
                                                                                    ak=self.ak, secret=self.secret,
                                                                                    region_id=self.region_id,
                                                                                    auto_retry=self.auto_retry,
                                                                                    max_retry_time=self.max_retry_time,
                                                                                    user_agent=self.user_agent,
                                                                                    port=self.port,
                                                                                    connect_timeout=self.connect_timeout,
                                                                                    timeout=self.timeout,
                                                                                    public_key_id=self.public_key_id,
                                                                                    private_key=self.private_key,
                                                                                    session_period=self.session_period,
                                                                                    credential=self.credential,
                                                                                    debug=self.debug,
                                                                                    verify=self.verify)

    class ProxyDefaultSdkCoreClient(AcsClient, object):

        def __init__(self, secret_name, ak_expire_handler, ak=None, secret=None,
                     region_id="cn-hangzhou",
                     auto_retry=True,
                     max_retry_time=None,
                     user_agent=None,
                     port=80,
                     connect_timeout=None,
                     timeout=None,
                     public_key_id=None,
                     private_key=None,
                     session_period=3600,
                     credential=None,
                     debug=False,
                     verify=None):
            self.secret_name = secret_name
            if ak_expire_handler is None:
                ak_expire_handler = SdkCoreAKExpireHandler()
            self.ak_expire_handler = ak_expire_handler
            self.rw_lock = RWLock()
            self.is_close = False
            super(SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient, self).__init__(ak=ak, secret=secret,
                                                                                               region_id=region_id,
                                                                                               auto_retry=auto_retry,
                                                                                               max_retry_time=max_retry_time,
                                                                                               user_agent=user_agent,
                                                                                               port=port,
                                                                                               connect_timeout=connect_timeout,
                                                                                               timeout=timeout,
                                                                                               public_key_id=public_key_id,
                                                                                               private_key=private_key,
                                                                                               session_period=session_period,
                                                                                               credential=credential,
                                                                                               debug=debug,
                                                                                               verify=verify)

        def _implementation_of_do_action(self, request, signer=None):
            try:
                self.rw_lock.read_acquire()
                status, headers, body, exception = super(SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient,
                                                         self)._implementation_of_do_action(request, signer)
                if isinstance(exception,
                              ServerException) and exception is not None and self.ak_expire_handler.judge_ak_expire(
                    exception):
                    AliyunSdkSecretsManagerPluginsManager.refresh_secret_info(self.secret_name)
                    return super(SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient,
                                 self)._implementation_of_do_action(
                        request,
                        signer)
                else:
                    return status, headers, body, exception
            finally:
                self.rw_lock.read_release()

        def __del__(self):
            super(SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient, self).__del__()

        def shutdown(self):
            if not self.is_close:
                self.is_close = True
                try:
                    AliyunSdkSecretsManagerPluginsManager.close_secretsmanager_plugin_updater_and_client(
                        self.secret_name, self)
                except Exception:
                    common_logger.get_logger().error("action:__del__", exc_info=True)

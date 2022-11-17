# coding=utf-8
from aliyunsdkcore.auth import credentials

from aliyun_sdk_secretsmanager_sdk_core_plugin.secretsmanager_sdk_core_plugin_manager import \
    SecretsManagerSdkCorePluginManager


class ProxyAcsClient(SecretsManagerSdkCorePluginManager.ProxyDefaultSdkCoreClient):

    def __init__(self, secret_name, ak_expire_handler=None, ak=None, secret=None, region_id="cn-hangzhou",
                 auto_retry=True, max_retry_time=None, user_agent=None, port=80, connect_timeout=None, timeout=None,
                 public_key_id=None, private_key=None, session_period=3600, credential=None, debug=False, verify=None):
        super(ProxyAcsClient, self).__init__(secret_name, ak_expire_handler, ak, secret, region_id, auto_retry,
                                             max_retry_time,
                                             user_agent, port, connect_timeout, timeout, public_key_id, private_key,
                                             session_period,
                                             credentials.AccessKeyCredential("", ""), debug, verify)
        self.__init_proxy_acsclient(secret_name, ak_expire_handler, region_id,
                                    auto_retry, max_retry_time, user_agent, port,
                                    connect_timeout, timeout,
                                    public_key_id, private_key, session_period,
                                    debug, verify)

    def __init_proxy_acsclient(self, secret_name, ak_expire_handler, region_id="cn-hangzhou",
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
                               verify=None):
        SecretsManagerSdkCorePluginManager.get_acs_client(secret_name,
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
                                                          verify=verify, ak_expire_handler=ak_expire_handler,
                                                          default_client=self)

    def __del__(self):
        super(ProxyAcsClient, self).__del__()

    def shutdown(self):
        super(ProxyAcsClient, self).shutdown()

阿里云Python SDK托管凭据插件
============================

阿里云Python
SDK的托管凭据插件可以帮助Python开发者更方便的利用托管在SecretsManager的RAM凭据，来访问阿里云服务的开放API。

*其他语言版本:*\ `English <README.rst>`__\ *,*\ `简体中文 <README.zh-cn.rst>`__

-  `阿里云托管RAM凭据主页 <https://help.aliyun.com/document_detail/212421.html>`__
-  `Issues <https://github.com/aliyun/aliyun-sdk-managed-credentials-providers-python/issues>`__
-  `Release <https://github.com/aliyun/aliyun-sdk-managed-credentials-providers-python/releases>`__
   ## 许可证

`Apache License
2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`__

优势
----

-  支持用户快速通过托管RAM凭据快速使用阿里云服务
-  支持多种认证鉴权方式如ECS实例RAM Role和Client Key
-  支持阿里云服务客户端自动刷新AK信息

软件要求
--------

-  您的凭据必须是托管RAM凭据
-  Python2.7.15+ 或 Python3.6+

背景
----

当您的应用程序通过阿里云SDK访问云服务时，访问凭证(Access
Keys)被用于认证应用的身份。访问凭据在使用中存在一定的安全风险，可能会被恶意的开发人员或外部威胁所利用。

阿里云凭据管家提供了帮助降低风险的解决方案，允许企业和组织集中管理所有应用程序的访问凭据，允许在不中断应用程序的情况下自动或手动轮转或者更新这些凭据。托管在SecretsManager的Access
Key被称为\ `托管RAM凭据 <https://help.aliyun.com/document_detail/212421.html>`__
。

使用凭据管家的更多优势，请参阅
`凭据管家概述 <https://help.aliyun.com/document_detail/152001.html>`__
。

客户端机制
----------

应用程序引用托管RAM凭据（Access Key）的\ ``凭据名称`` 。

托管凭据插件定期从SecretsManager获取由\ ``凭据名称``\ 代表的Access
Key，并提供给阿里云SDK，应用则使用SDK访问阿里云开放API。插件以指定的间隔（可配置）刷新缓存在内存中的Access
Key。

在某些情况下，缓存的访问凭据不再有效，这通常发生在管理员在凭据管家中执行紧急访问凭据轮转以响应泄漏事件时。使用无效访问凭据调用OpenAPI通常会导致与API错误代码对应的异常。如果相应的错误代码为\ ``InvalidAccessKeyId.NotFound``\ 或\ ``InvalidAccessKeyId``\ ，则托管凭据插件将立即刷新缓存的Access
Key，随后重试失败的OpenAPI调用。

如果使用过期Access
Key调用某些云服务API返回的错误代码和上述所列错误码相异，应用开发人员则可以修改默认的错误重试行为。请参阅\ `修改默认过期处理程序 <#修改默认过期处理程序>`__
。


安装
----

通过pip安装官方发布的版本（以Linux系统为例）：

.. code:: bash

       $ pip install aliyun-openapi-python-sdk-managed-credentials-provider

也可以直接安装解压后的安装包：

.. code:: bash

       $ sudo python setup.py install

支持阿里云云产品
----------------

阿里云SDK托管凭据Python插件支持以下云产品:

+-------------+-------------+-------------+-------------+-------------+
| 阿          | SDK         | 支持版本    | 插件名称    | 导入插件mav |
| 里云SDK名称 | 模块名称    |             |             | en(groupId: |
|             |             |             |             | artifactId) |
+=============+=============+=============+=============+=============+
| 阿里云SDK   | aliyun-pyth | >=2.13.30   | `阿         | aliyun-     |
|             | on-sdk-core |             | 里云Python  | python-sdk- |
|             |             |             | SDK托管     | core-manage |
|             |             |             | 凭据插件 <h | d-credentia |
|             |             |             | ttps://gith | ls-provider |
|             |             |             | ub.com/aliy |             |
|             |             |             | un/aliyun-s |             |
|             |             |             | dk-managed- |             |
|             |             |             | credentials |             |
|             |             |             | -providers- |             |
|             |             |             | python/tree |             |
|             |             |             | /master/ali |             |
|             |             |             | yun-sdk-man |             |
|             |             |             | aged-creden |             |
|             |             |             | tials-provi |             |
|             |             |             | ders/aliyun |             |
|             |             |             | -openapi-py |             |
|             |             |             | thon-sdk-ma |             |
|             |             |             | naged-crede |             |
|             |             |             | ntials-prov |             |
|             |             |             | ider>`__    |             |
+-------------+-------------+-------------+-------------+-------------+
| OSS Python  | oss2        | >=2.7.0     | `OSS Python | aliyun-sdk  |
| SDK         |             |             | SDK托管凭据 | -oss-manage |
|             |             |             | 插件 <https | d-credentia |
|             |             |             | ://github.c | ls-provider |
|             |             |             | om/aliyun/a |             |
|             |             |             | liyun-sdk-m |             |
|             |             |             | anaged-cred |             |
|             |             |             | entials-pro |             |
|             |             |             | viders-pyth |             |
|             |             |             | on/tree/mas |             |
|             |             |             | ter/aliyun- |             |
|             |             |             | sdk-managed |             |
|             |             |             | -credential |             |
|             |             |             | s-providers |             |
|             |             |             | /aliyun-oss |             |
|             |             |             | -python-sdk |             |
|             |             |             | -managed-cr |             |
|             |             |             | edentials-p |             |
|             |             |             | rovider>`__ |             |
+-------------+-------------+-------------+-------------+-------------+

使用示例
--------

步骤1：配置托管凭据插件
~~~~~~~~~~~~~~~~~~~~~~~

``managed_credentials_providers.properties``\ (在程序运行目录下)初始化阿里云凭据管家动态RAM凭据客户端：

-  访问DKMS，你必须要设置如下系统环境变量 (linux):
   ``properties     cache_client_dkms_config_info=[{"ignoreSslCerts":false,"passwordFromFilePathName":"client_key_password_from_file_path","clientKeyFile":"\<your client key file absolute path>","regionId":"\<your dkms region>","endpoint":"\<your dkms endpoint>"}]``
    cache_client_dkms_config_info配置项解释:
    1.cache_client_dkms_config_info配置项为数组，支持配置多个region实例
    2.ignoreSslCerts:是否忽略ssl证书 (true:忽略ssl证书,false:验证ssl证书)
    3.passwordFromFilePathName和passwordFromEnvVariable
      passwordFromFilePathName:client key密码配置从文件中获取，与passwordFromEnvVariable二选一
      例:当配置"passwordFromFilePathName":"client_key_password_from_file_path"时，
        需在环境变量中添加client_key_password_from_file_path=<你的client key密码文件所在的绝对路径>，
        以及对应写有password的文件。
      passwordFromEnvVariable:client key密码配置从环境变量中获取，与passwordFromFilePathName二选一
      例:当配置"passwordFromEnvVariable":"client_key_password_from_env_variable"时，
        需在环境变量中添加client_key_password_from_env_variable=<你的client key密码对应的环境变量名>
        以及对应的环境变量(xxx_env_variable=<your password>)。
    4.clientKeyFile:client key json文件的绝对路径
    5.regionId:地域Id
    6.endpoint:专属kms的域名地址
    ``

步骤 2：使用托管凭据插件访问云服务
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

您可以通过以下代码通过凭据管家托管RAM凭据使用阿里云SDK客户端。

.. code:: python

   from aliyun_sdk_secretsmanager_sdk_core_plugin.proxy_acs_client import ProxyAcsClient

   region="cn-hangzhou"
   secretName="******"

   # 获取ACSClient
   client = ProxyAcsClient(region_id=region, secret_name=secretName )

   # 业务方业务代码：调用阿里云服务实现业务功能
   invoke(client,region)

   # 通过下面方法关闭客户端来释放插件关联的资源
   client.shutdown()

修改默认过期处理程序
--------------------

在支持用户自定义错误重试的托管凭据Python插件中，用户可以自定义客户端因凭据手动轮转极端场景下的错误重试判断逻辑，只实现以下接口即可。

.. code:: python

   import abc


   class AKExpireHandler(object):
     __metaclass__ = abc.ABCMeta

     @abc.abstractmethod
     def judge_ak_expire(self, exception):
         """判断异常是否由Ak过期引起"""
         pass

下面代码示例是用户自定义判断异常接口和使用自定义判断异常实现访问云服务。

.. code:: python

   from aliyun_sdk_secretsmanager_common_plugin.ak_expire_handler import AKExpireHandler

   AK_EXPIRE_ERROR_CODE = "InvalidAccessKeyId.NotFound"


   class AliyunSdkAKExpireHandler(AKExpireHandler):

     def __init__(self, ak_expire_error_code=None):
         if ak_expire_error_code is None or ak_expire_error_code is "":
             self.ak_expire_error_code = AK_EXPIRE_ERROR_CODE
         else:
             self.ak_expire_error_code = ak_expire_error_code

     def judge_ak_expire(self, exception):
         if self.get_ak_expire_code() == self.get_error_code(exception):
             return True
         return False

     def get_error_code(self, exception):
         return exception.error_code

     def get_ak_expire_code(self):
         return self.ak_expire_error_code


   from aliyun_sdk_secretsmanager_sdk_core_plugin.proxy_acs_client import ProxyAcsClient

   region = "cn-hangzhou"
   secretName = "******"

   # 获取ACSClient
   client = ProxyAcsClient(region_id=region, secret_name=secretName,
                         ak_expire_handler=AliyunSdkAKExpireHandler("InvalidAccessKeyId.NotFound"))

   # 业务方业务代码：调用阿里云服务实现业务功能
   invoke(client, region)

   # 通过下面方法关闭客户端来释放插件关联的资源
   client.shutdown()

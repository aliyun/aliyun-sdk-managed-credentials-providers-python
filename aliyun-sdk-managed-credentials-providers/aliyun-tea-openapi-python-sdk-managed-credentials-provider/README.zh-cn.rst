阿里云 Tea OpenAPI Python SDK托管凭据插件
=========================================

阿里云 Tea OpenAPI Python
SDK的托管凭据插件可以帮助Python开发者更方便的利用托管在SecretsManager的RAM凭据，来访问阿里云服务的开放API。您可以通过Maven快速使用。\ `查看可使用的云产品列表 <https://github.com/aliyun/alibabacloud-python-sdk>`__

*其他语言版本:*\ `English <README.md>`__\ *,*\ `简体中文 <README.zh-cn.md>`__

背景
----

当您的应用程序通过阿里云 Tea OpenAPI SDK访问云服务时，访问凭证(Access
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

托管凭据插件定期从SecretsManager获取由\ ``凭据名称``\ 代表的AccessKey，并提供给阿里云SDK，应用则使用SDK访问阿里云开放API。插件以指定的间隔（可配置）刷新缓存在内存中的Access
Key。

在某些情况下，缓存的访问凭据不再有效，这通常发生在管理员在凭据管家中执行紧急访问凭据轮转以响应泄漏事件时。使用无效访问凭据调用OpenAPI通常会导致与API错误代码对应的异常。如果相应的错误代码为\ ``InvalidAccessKeyId.NotFound``\ 、\ ``InvalidAccessKeyId``\ 或\ ``Unauthorized``\ ，则托管凭据插件将立即刷新缓存的Access
Key，随后重试失败的OpenAPI调用。

如果使用过期AccessKey调用某些云服务API返回的错误代码和上述所列错误码相异，应用开发人员则可以修改默认的错误重试行为。请参阅\ `修改默认过期处理程序 <#修改默认过期处理程序>`__
。

软件要求
--------

Python3.6+

安装
----

通过pip安装官方发布的版本（以Linux系统为例）：

.. code:: bash

   $ pip install aliyun_tea_openapi_python_sdk_managed_credentials_provider

也可以直接安装解压后的安装包：

.. code:: bash

   $ sudo python setup.py install

使用示例(以ECS为例)
-------------------

步骤 1：安装ECS SDK
~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ pip install alibabacloud_ecs20140526

步骤 2：配置托管凭据插件
~~~~~~~~~~~~~~~~~~~~~~~~

``managed_credentials_providers.properties``\ (在程序运行目录下)初始化阿里云凭据管家动态RAM凭据客户端：

.. code:: properties

   cache_client_dkms_config_info=[{"regionId":"<your dkms region>","endpoint":"<your dkms endpoint>","passwordFromFilePath":"< your password file path >","clientKeyFile":"<your client key file path>","ignoreSslCerts":false,"caFilePath":"<your CA certificate file path>"}]

::

   cache_client_dkms_config_info配置项说明:
   1. cache_client_dkms_config_info配置项为json数组，支持配置多个region实例
   2. regionId:地域Id
   3. endpoint:专属kms的域名地址
   4. passwordFromFilePath和passwordFromEnvVariable
      passwordFromFilePath:client key密码配置从文件中获取，与passwordFromEnvVariable二选一
      例:当配置passwordFromFilePath:<你的client key密码文件所在的路径>,需在配置的绝对路径下配置写有password的文件
      passwordFromEnvVariable:client key密码配置从环境变量中获取，与passwordFromFilePath二选一
      例:当配置"passwordFromEnvVariable":"your_password_env_variable"时，
        需在环境变量中添加your_password_env_variable=<你的client key对应的密码>
   5. clientKeyFile:client key json文件的路径
   6. ignoreSslCerts:是否忽略ssl证书 (true:忽略ssl证书,false:验证ssl证书)
   7. caFilePath:专属kms的CA证书路径

步骤 3：使用托管凭据插件访问云服务
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

您可以通过以下代码通过凭据管家托管RAM凭据使用阿里云SDK客户端。

.. code:: python

   from alibabacloud_ecs20140526 import models as ecs_20140526_models
   from aliyun_sdk_secretsmanager_tea_openapi_plugin import proxy_client_creator
   from alibabacloud_tea_openapi import models as open_api_models
   from alibabacloud_ecs20140526.client import Client

   secret_name = "******"
   # 自定义配置文件
   # from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader
   # ConfigLoader.set_config_name("custom-config")
   config = open_api_models.Config(endpoint="ecs-endpoint")
   client = proxy_client_creator.create_client_with_config(config, Client, secret_name)
   describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(region_id='cn-hangzhou')
   response = client.describe_instances(describe_instances_request)
   print(response.body)

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

   class TeaOpenApiAKExpireHandler(AKExpireHandler):
       AK_EXPIRE_ERROR_CODES = ["InvalidAccessKeyId.NotFound", "InvalidAccessKeyId"，"Unauthorized"]

       def __init__(self, ak_expire_error_codes=None):
           if ak_expire_error_codes is None or len(ak_expire_error_codes) == 0:
               self.error_code_set = set(self.AK_EXPIRE_ERROR_CODES)
           else:
               self.error_code_set = set(ak_expire_error_codes)

       def judge_ak_expire(self, exception) -> bool:
           return exception.code in self.error_code_set

   from alibabacloud_ecs20140526 import models as ecs_20140526_models
   from aliyun_sdk_secretsmanager_tea_openapi_plugin import proxy_client_creator
   from alibabacloud_tea_openapi import models as open_api_models
   from alibabacloud_ecs20140526.client import Client

   secret_name = "******"
   # 自定义配置文件
   # from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader
   # ConfigLoader.set_config_name("custom-config")
   config = open_api_models.Config(endpoint="ecs-endpoint")
   client = proxy_client_creator.create_client_with_config(config, Client, secret_name,TeaOpenApiAKExpireHandler(["InvalidAccessKeyId.NotFound", "InvalidAccessKeyId"，"Unauthorized"]))
   describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(region_id='cn-hangzhou')
   response = client.describe_instances(describe_instances_request)
   print(response.body)

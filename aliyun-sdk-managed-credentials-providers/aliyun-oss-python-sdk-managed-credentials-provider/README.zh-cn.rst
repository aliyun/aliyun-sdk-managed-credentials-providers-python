OSS Python SDK托管凭据插件
==========================

OSS Python
SDK托管凭据插件可以使Python开发者通过托管RAM凭据快速使用阿里云OSS服务。

*其他语言版本:*\ `English <README.rst>`__\ *,*\ `简体中文 <README.zh-cn.rst>`__

背景
----

当您的应用程序通过阿里云OSS SDK访问OSS时，访问凭证(Access
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
Key，并提供给阿里云 OSS
SDK，应用则使用SDK访问OSS服务。插件以指定的间隔（可配置）刷新缓存在内存中的Access
Key。

软件要求
--------

Python2.7.15+ 或 Python3.5+

安装
----

通过pip安装官方发布的版本（以Linux系统为例）：

.. code:: bash

       $ pip install aliyun-oss-python-sdk-managed-credentials-provider

也可以直接安装解压后的安装包：

.. code:: bash

       $ sudo python setup.py install

使用示例
--------

步骤1：配置托管凭据插件
~~~~~~~~~~~~~~~~~~~~~~~

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

步骤 2：使用托管凭据插件访问OSS服务
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

您可以通过以下代码通过凭据管家动态RAM凭据使用阿里云OSS客户端。

.. code:: python

   from aliyun_sdk_secretsmanager_oss_plugin.proxy_bucket import ProxyBucket
   from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader
   from itertools import islice

   endpoint = "******"
   secret_name ="******"
   bucket_name = "******"
   //自定义配置文件
   //ConfigLoader.set_config_name("custom-config")
   bucket = ProxyBucket(secret_name=secret_name, endpoint=endpoint, bucket_name=bucket_name)
   objects = bucket.list_objects()
   for b in islice(objects.object_list, 10):
       print(b.key)
   bucket.shutdown()

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

    import oss2

    from aliyun_sdk_secretsmanager_common_plugin.ak_expire_handler import AKExpireHandler

    AK_EXPIRE_ERROR_CODE = "InvalidAccessKeyId"


    class OssAkExpireHandler(AKExpireHandler):
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
            if isinstance(exception, oss2.exceptions.ServerError):
                if exception.details is not None:
                    return exception.details.get('Code', '')
            return ""

        def get_ak_expire_code(self):
            return self.ak_expire_error_code


   from aliyun_sdk_secretsmanager_oss_plugin.proxy_bucket import ProxyBucket
   from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader

   from itertools import islice

   endpoint = "******"
   secret_name ="******"
   bucket_name = "******"
   //自定义配置文件
   //ConfigLoader.set_config_name("custom-config")
   bucket = ProxyBucket(secret_name=secret_name, endpoint=endpoint, bucket_name=bucket_name,ak_expire_handler=OssAkExpireHandler())
   objects = bucket.list_objects()
   for b in islice(objects.object_list, 10):
       print(b.key)
   bucket.shutdown()

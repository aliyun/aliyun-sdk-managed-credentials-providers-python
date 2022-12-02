The Aliyun SDK Managed Credentials Providers for Python
==================================================

The Aliyun SDK Managed Credentials Providers for Python enables Python
developers to easily access to other Aliyun Services using managed RAM
credentials stored in Aliyun Secrets Manager.

Read this in other languages: `English <README.rst>`__,
`简体中文 <README.zh-cn.rst>`__

-  `Aliyun Secrets Manager Managed RAM Credentials
   Summary <https://www.alibabacloud.com/help/doc-detail/152001.htm>`__
-  `Issues <https://github.com/aliyun/aliyun-sdk-managed-credentials-providers-python/issues>`__
-  `Release <https://github.com/aliyun/aliyun-sdk-managed-credentials-providers-python/releases>`__

License
-------

`Apache License
2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`__

Features
--------

-  Provide an easy method to other AliCould Services using managed RAM
   credentials
-  Provides multiple access ways such as ECS instance RAM Role or Client
   Key to obtain a managed RAM credentials
-  Provides the Aliyun Service client to refresh the RAM credentials
   automatically

Requirements
------------

-  Your secret must be a managed RAM credentials
-  Python 2.7.15 or later and Python 3.6 or later

Background
----------

When applications use Aliyun SDK to call Alibaba Cloud Open APIs, access
keys are traditionally used to authenticate to the cloud service. While
access keys are easy to use they present security risks that could be
leveraged by adversarial developers or external threats.

Alibaba Cloud SecretsManager is a solution that helps mitigate the risks
by allowing organizations centrally manage access keys for all
applications, allowing automatically or mannually rotating them without
interrupting the applications. The managed access keys in SecretsManager
is called `Managed RAM
Credentials <https://www.alibabacloud.com/help/doc-detail/212421.htm>`__.

For more advantages of using SecretsManager, refer to `SecretsManager
Overview <https://www.alibabacloud.com/help/doc-detail/152001.htm>`__.

Client Mechanism
----------------

Applications use the access key that is managed by SecretsManager via
the ``Secret Name`` representing the access key.

The Managed Credentials Provider periodically obtains the Access Key
represented by the secret name and supply it to Aliyun SDK when
accessing Alibaba Cloud Open APIs. The provider normally refreshes the
locally cached access key at a specified interval, which is
configurable.

However, there are circumstances that the cached access key is no longer
valid, which typically happens when emergent access key rotation is
performed by adminstrators in SecretsManager to respond to a leakage
incident. Using invalid access key to call Open APIs usually results in
an exception that corresponds to an API error code. The Managed
Credentials Provider will immediately refresh the cached access key and
retry the failed Open API if the corresponding error code is
``InvalidAccessKeyId.NotFound`` or ``InvalidAccessKeyId``.

Application developers can override or extend this behavior for specific
cloud services if the APIs return other error codes for using expired
access keys. Refer to `Modifying the default expire
handler <#modifying-the-default-expire-handler>`__.

Install
-------

Install the official release version through PIP (taking Linux as an
example):

.. code:: bash

       $ pip install aliyun-openapi-python-sdk-managed-credentials-provider

You can also install the unzipped installer package directly:

.. code:: bash

       $ sudo python setup.py install

Support Aliyun Services
-----------------------

The Aliyun SDK Managed Credentials Providers for Python supports the
following Aliyun Services:

+-------------+-------------+-------------+-------------+-------------+
| Aliyun SDK  | SDK module  | Supported   | Plugin Name | Import      |
| Name        | name        | Versions    |             | plugin      |
|             |             |             |             | mav         |
|             |             |             |             | en(groupId: |
|             |             |             |             | artifactId) |
+=============+=============+=============+=============+=============+
| Alibaba     | aliyun-pyth | >=2.13.30   | `Managed    | aliyun-     |
| Cloud SDK   | on-sdk-core |             | Credentials | python-sdk- |
|             |             |             | Provider    | core-manage |
|             |             |             | for Aliyun  | d-credentia |
|             |             |             | Python      | ls-provider |
|             |             |             | SDK <h      |             |
|             |             |             | ttps://gith |             |
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
|             |             |             | thon-sd     |             |
|             |             |             | k-manage    |             |
|             |             |             | d-credentia |             |
|             |             |             | ls-provide  |             |
|             |             |             | r>`__       |             |
+-------------+-------------+-------------+-------------+-------------+
| OSS SDK     | oss2        | >=2.7.0     | `Managed    | aliyun-sdk  |
|             |             |             | Credentials | -oss-manage |
|             |             |             | Provider    | d-credentia |
|             |             |             | for Aliyun  | ls-provider |
|             |             |             | OSS         |             |
|             |             |             | SDK <https  |             |
|             |             |             | ://github.c |             |
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

Aliyun SDK Managed Credentials Provider Sample
----------------------------------------------

Step 1: Configure the credentials provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``managed_credentials_providers.properties`` (it exists in the program
running directory) to initialize the Aliyun SDK Managed Credentials
Providers:

-  Access aliyun dedicated kms, you must set the following system
   environment variables (for linux):
   ``properties     cache_client_dkms_config_info=[{"ignoreSslCerts":false,"passwordFromFilePathName":"client_key_password_from_file_path","clientKeyFile":"\<your client key file absolute path>","regionId":"\<your dkms region>","endpoint":"\<your dkms endpoint>"}]``
    The details of the configuration item named cache_client_dkms_config_info:
    1.The cache_client_dkms_config_info configuration item is an array, you can configure multiple region instances
    2.ignoreSslCerts:If ignore ssl certs (true: Ignores the ssl certificate, false: Validates the ssl certificate)
    3.passwordFromFilePathName and passwordFromEnvVariable
      passwordFromFilePathName:The client key password configuration is obtained from the file,choose one of the two with passwordFromEnvVariable.
      e.g.  Where configuring "passwordFromFilePathName": "client_key_password_from_file_path",
            You need to add properties client_key_password_from_file_path=< your password file absolute path >  in the configuration file.
            and correspond to a file with a password written on it.
      passwordFromEnvVariable:The client key password configuration is obtained from the environment variable,choose one of the two with passwordFromFilePathName.
      e.g.  Where configuring "passwordFromEnvVariable": "client_key_password_from_env_variable",
            You need to add client_key_password_from_env_variable=< your client key private key password from environment variable > in env
            and the corresponding env variable (xxx_env_variable=<your password>).
    4.clientKeyFile:The absolute path to the client key json file
    5.regionId:Region id
    6.endpoint:Domain address of dkms
    ``

Step 2: Use the credentials provider in Aliyun SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You could use the following code to access Aliyun services with managed
RAM credentials。

.. code:: python

   from aliyun_sdk_secretsmanager_sdk_core_plugin.proxy_acs_client import ProxyAcsClient

   region="cn-hangzhou"
   secretName="******"

   # get an ACSClient
   client = ProxyAcsClient(region_id=region, secret_name=secretName )

   # business code: your code that calls Cloud Open API
   invoke(client,region)

   # must use the follow method to close the client for releasing provider resource
   client.shutdown()

Modifying the default expire handler
------------------------------------

With Aliyun SDK Managed Credentials Provider that supports customed
error retry, you can customize the error retry judgment of the client
due to manual rotation of credentials in extreme scenarios, you only
implement the following interface.

.. code:: python

   import abc


   class AKExpireHandler(object):
     __metaclass__ = abc.ABCMeta

     @abc.abstractmethod
     def judge_ak_expire(self, exception):
         """judge whether the exception is caused by AccessKey expiration"""
         pass

The sample codes below show customed judgment exception interface and
use it to call aliyun services.

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

   # get an ACSClient
   # provide the given error codes to obtain the credentials again
   client = ProxyAcsClient(region_id=region, secret_name=secretName,
                           ak_expire_handler=AliyunSdkAKExpireHandler("InvalidAccessKeyId.NotFound"))

   # business code: your code that calls Cloud Open API
   invoke(client, region)

   # must use the follow method to close the client
   client.shutdown()

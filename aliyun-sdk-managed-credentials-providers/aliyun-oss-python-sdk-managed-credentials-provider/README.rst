Managed Credentials Provider for Aliyun Python OSS SDK
======================================================

The Managed Credentials Provider for Aliyun Python OSS SDK enables
Python developers to easily access to Aliyun OSS Services using managed
RAM credentials stored in Aliyun Secrets Manager.

Read this in other languages: `English <README.rst>`__,
`简体中文 <README.zh-cn.rst>`__

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
represented by the secret name and supply it to Aliyun OSS SDK when
accessing Alibaba Cloud OSS services. The provider normally refreshes
the locally cached access key at a specified interval, which is
configurable.

Requirements
------------

Python 2.7.15 or later and Python 3.5 or later

Install
-------

Install the official release version through PIP (taking Linux as an
example):

.. code:: bash

       $ pip install aliyun-oss-python-sdk-managed-credentials-provider

You can also install the unzipped installer package directly:

.. code:: bash

       $ sudo python setup.py install

Aliyun OSS SDK Managed Credentials Provider Sample
--------------------------------------------------

Step 1: Configure the credentials provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``managed_credentials_providers.properties`` (it exists in the program
running directory) to initialize the Aliyun SDK Managed Credentials
Providers:

.. code:: properties

    cache_client_dkms_config_info=[{"regionId":"<your dkms region>","endpoint":"<your dkms endpoint>","passwordFromFilePath":"< your password file path >","clientKeyFile":"<your client key file path>","ignoreSslCerts":false,"caFilePath":"<your CA certificate file path>"}]

::

       The details of the configuration item named cache_client_dkms_config_info:
       1. The configuration item named cache_client_dkms_config_info must be configured as a json array, you can configure multiple region instances
       2. regionId:Region id
       3. endpoint:Domain address of dkms
       4. passwordFromFilePath and passwordFromEnvVariable
         passwordFromFilePath:The client key password configuration is obtained from the file,choose one of the two with passwordFromEnvVariable.
         e.g. while configuring passwordFromFilePath: < your password file path >, you need to configure a file with password written under the configured path
         passwordFromEnvVariable:The client key password configuration is obtained from the environment variable,choose one of the two with passwordFromFilePath.
         e.g. while configuring passwordFromEnvVariable: "your_password_env_variable",
              You need to add your_password_env_variable=< your client key private key password > in env.
       5. clientKeyFile:The path to the client key json file
       6. ignoreSslCerts:If ignore ssl certs (true: Ignores the ssl certificate, false: Validates the ssl certificate)
       7. caFilePath:The path of the CA certificate of the dkms

Step 2: Use the credentials provider in Aliyun OSS SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You cloud use the following code to access OSS services with managed RAM
credentials.

.. code:: python

   from aliyun_sdk_secretsmanager_oss_plugin.proxy_bucket import ProxyBucket
   from itertools import islice

   endpoint = "******"
   secret_name ="******"
   bucket_name = "******"
   bucket = ProxyBucket(secret_name=secret_name, endpoint=endpoint, bucket_name=bucket_name)
   objects = bucket.list_objects()
   for b in islice(objects.object_list, 10):
       print(b.key)
   bucket.shutdown()

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
   from itertools import islice

   endpoint = "******"
   secret_name ="******"
   bucket_name = "******"
   bucket = ProxyBucket(secret_name=secret_name, endpoint=endpoint, bucket_name=bucket_name,ak_expire_handler=OssAkExpireHandler())
   objects = bucket.list_objects()
   for b in islice(objects.object_list, 10):
       print(b.key)
   bucket.shutdown()

Aliyun Tea OpenAPI Python SDK Managed Credentials Plugin
========================================================

Aliyun Tea OpenAPI Python SDK Managed Credentials Plugin helps Python
developers more easily use RAM credentials managed in SecretsManager to
access Aliyun service APIs. You can quickly use it via Maven. `View list
of supported cloud
products <https://github.com/aliyun/alibabacloud-python-sdk>`__

Read this in other languages: `English <README.md>`__,
`简体中文 <README.zh-cn.md>`__

Background
----------

When applications use Aliyun Tea OpenAPI SDK to call Alibaba Cloud Open
APIs, access keys are traditionally used to authenticate to the cloud
service. While access keys are easy to use they present security risks
that could be leveraged by adversarial developers or external threats.

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
``InvalidAccessKeyId.NotFound`` ，\ ``InvalidAccessKeyId`` or
``Unauthorized``.

Application developers can override or extend this behavior for specific
cloud services if the APIs return other error codes for using expired
access keys. Refer to `Modifying the default expire
handler <#modifying-the-default-expire-handler>`__.

Requirements
------------

Python 3.6 or later

Install
-------

Install the official release version through PIP (taking Linux as an
example):

.. code:: bash

   $ pip install aliyun-tea-openapi-python-sdk-managed-credentials-provider

You can also install the unzipped installer package directly:

.. code:: bash

   $ sudo python setup.py install

Aliyun SDK Managed Credentials Provider Sample(ECS as an example)
-----------------------------------------------------------------

Step 1: Install ECS SDK
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   $ pip install alibabacloud_ecs20140526

Step 2: Configure the credentials provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialize the dynamic RAM credential client of Alibaba Cloud Credential
Manager using the managed_credentials_providers.properties file (in the
program’s running directory):

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

Step 3: Use the Managed Credentials Plugin to Access Aliyun Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You could use the following code to access Aliyun services with managed
RAM credentials。

.. code:: python

   from alibabacloud_ecs20140526 import models as ecs_20140526_models
   from aliyun_sdk_secretsmanager_tea_openapi_plugin import proxy_client_creator
   from alibabacloud_tea_openapi import models as open_api_models
   from alibabacloud_ecs20140526.client import Client

   secret_name = "******"
   # Custom configuration file
   # from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader
   # ConfigLoader.set_config_name("custom-config")
   config = open_api_models.Config(endpoint="ecs-endpoint")
   client = proxy_client_creator.create_client_with_config(config, Client, secret_name)
   describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(region_id='cn-hangzhou')
   response = client.describe_instances(describe_instances_request)
   print(response.body)

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
   # Custom configuration file
   # from aliyun_sdk_secretsmanager_common_plugin.utils.config_loader import ConfigLoader
   # ConfigLoader.set_config_name("custom-config")
   config = open_api_models.Config(endpoint="ecs-endpoint")
   client = proxy_client_creator.create_client_with_config(config, Client, secret_name,TeaOpenApiAKExpireHandler(["InvalidAccessKeyId.NotFound", "InvalidAccessKeyId"，"Unauthorized"]))
   describe_instances_request = ecs_20140526_models.DescribeInstancesRequest(region_id='cn-hangzhou')
   response = client.describe_instances(describe_instances_request)
   print(response.body)

# coding=utf-8
from aliyun_sdk_secretsmanager_common_plugin.default_ak_expire_handler import DefaultAKExpireHandler

AK_EXPIRE_ERROR_CODE = "InvalidAccessKeyId.NotFound"


class SdkCoreAKExpireHandler(DefaultAKExpireHandler):
    def __init__(self, ak_expire_error_code=None):
        if ak_expire_error_code is None or ak_expire_error_code is "":
            self.ak_expire_error_code = AK_EXPIRE_ERROR_CODE
        else:
            self.ak_expire_error_code = ak_expire_error_code

    def get_error_code(self, exception):
        return exception.error_code

    def get_ak_expire_code(self):
        return self.ak_expire_error_code

# coding=utf-8
from aliyun_sdk_secretsmanager_common_plugin.default_temp_ak_expire_handler import DefaultTempAKExpireHandler

TEMP_AK_EXPIRE_ERROR_CODE = "InvalidAccessKeyId.NotFound"


class SdkCoreTempAKExpireHandler(DefaultTempAKExpireHandler):
    def __init__(self, tmp_ak_expire_error_code=None):
        if tmp_ak_expire_error_code is None or tmp_ak_expire_error_code is "":
            self.tmp_ak_expire_error_code = TEMP_AK_EXPIRE_ERROR_CODE
        else:
            self.tmp_ak_expire_error_code = tmp_ak_expire_error_code

    def get_error_code(self, exception):
        return exception.error_code

    def get_temp_ak_expire_code(self):
        return self.tmp_ak_expire_error_code

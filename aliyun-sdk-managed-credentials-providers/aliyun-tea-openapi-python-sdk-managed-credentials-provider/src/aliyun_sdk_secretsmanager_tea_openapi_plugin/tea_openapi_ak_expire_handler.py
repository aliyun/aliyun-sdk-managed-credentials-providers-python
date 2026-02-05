# coding=utf-8
from aliyun_sdk_secretsmanager_common_plugin.ak_expire_handler import AKExpireHandler


class TeaOpenApiPluginAKExpireHandler(AKExpireHandler):
    AK_EXPIRE_ERROR_CODES = ["InvalidAccessKeyId.NotFound", "InvalidAccessKeyId", "Unauthorized"]

    def __init__(self, ak_expire_error_codes=None):
        if ak_expire_error_codes is None or len(ak_expire_error_codes) == 0:
            self.error_code_set = set(self.AK_EXPIRE_ERROR_CODES)
        else:
            self.error_code_set = set(ak_expire_error_codes)

    def judge_ak_expire(self, exception) -> bool:
        return exception.code in self.error_code_set

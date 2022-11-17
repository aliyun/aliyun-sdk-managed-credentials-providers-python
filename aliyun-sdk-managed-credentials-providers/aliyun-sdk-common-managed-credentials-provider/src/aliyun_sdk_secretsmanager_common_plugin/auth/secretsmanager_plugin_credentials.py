# coding=utf-8
import sys


class SecretsManagerPluginCredentials(object):

    def __init__(self, access_key_id, access_key_secret, expire_timestamp, generate_timestamp=sys.maxsize):
        if access_key_id is None or access_key_id == "":
            raise ValueError("Access key ID cannot be null.")
        if access_key_secret is None or access_key_secret == "":
            raise ValueError("Access key secret cannot be null.")
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.expire_timestamp = expire_timestamp
        self.generate_timestamp = generate_timestamp

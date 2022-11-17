# coding=utf-8
from alibaba_cloud_secretsmanager_client.utils import common_logger


def add_message(queue, monitor_message_info):
    try:
        queue.put(monitor_message_info, True)
        if monitor_message_info.alarm:
            common_logger.get_logger().error(
                "execute %s secret_name:%s error_message:%s" % (
                    monitor_message_info.action, monitor_message_info.secret_name,
                    monitor_message_info.error_message))
    except Exception:
        pass

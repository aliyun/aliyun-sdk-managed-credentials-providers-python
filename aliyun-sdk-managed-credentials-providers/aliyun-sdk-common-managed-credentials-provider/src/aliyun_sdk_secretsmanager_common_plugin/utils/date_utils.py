# coding=utf-8
import time

TIMEZONE_DATE_PATTERN = "%Y-%m-%dT%H:%M:%SZ"


def format_date(date, pattern):
    return time.strftime(pattern, time.localtime(date + time.timezone))


def parse_date(date_str, pattern):
    return time.mktime(time.strptime(date_str, pattern)) - time.timezone

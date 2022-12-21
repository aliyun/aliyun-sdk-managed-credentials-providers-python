# coding=utf-8
# !/usr/bin/python

"""Aliyun SDK Secrets Manager SDK Core Plugin for Python."""
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*args):
    """Reads complete file contents."""
    return open(os.path.join(HERE, *args), 'rb').read().decode(encoding="utf-8")


setup(
    name="aliyun-openapi-python-sdk-managed-credentials-provider",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version="0.1.0",
    license="Apache License 2.0",
    author="Aliyun",
    maintainer="Aliyun",
    description="Managed Credentials Provider for Aliyun Python SDK",
    keywords=["aliyun", "kms", "secretsmanager"],
    install_requires=[
        'aliyun-sdk-common-managed-credentials-provider>=0.1.0'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Security",
    ],
)

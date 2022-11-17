# coding=utf-8
# !/usr/bin/python

"""Aliyun SDK Secrets Manager Common Plugin for Python."""
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*args):
    """Reads complete file contents."""
    return open(os.path.join(HERE, *args), 'rb').read().decode(encoding="utf-8")


setup(
    name="aliyun-sdk-common-managed-credentials-provider",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version="0.0.5",
    license="Apache License 2.0",
    author="Aliyun",
    maintainer="Aliyun",
    description="Aliyun SDK Common Managed Credentials Provider",
    keywords=["aliyun", "kms", "common"],
    install_requires=[
    	"protobuf<=3.17.0; python_version<='3.6'",
        "protobuf<=3.20.0; python_version>='3.7'",
        "requests<=2.0.0; python_version=='2.7'",
        "requests>=0.10.1; python_version>='3'",
        "cryptography<=3.3.0; python_version=='2.7'",
        "cryptography<=38.0.0; python_version>='3'",
        "pyopenssl<=21.0.0; python_version=='2.7'",
        "multidict<=5.1.0; python_version>='3'",
        "apscheduler<=3.8.0",
        "aliyun-secret-manager-client>=0.0.6",
        "typing_extensions <= 4.1.1"
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
        "Topic :: Security"
    ],
)

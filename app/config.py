#!/usr/bin/env python
"""
Configurations
"""


class BaseConfig(object):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017


class TestConfig(BaseConfig):
    TESTING = True

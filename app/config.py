#!/usr/bin/env python
"""
Configurations
"""

class BaseConfig(object):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = False


class TestConfig(TestConfig):
    TESTING = True


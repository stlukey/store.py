#!/usr/bin/env python
"""
Configurations
"""

from .modules.products.queries import categories_get_all

class GlobalTemplateVars(object):
    def __init__(self, app):
        self.app = app

    categories = property(lambda self: categories_get_all(self.app.db))


class BaseConfig(object):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017


class TestConfig(BaseConfig):
    TESTING = True

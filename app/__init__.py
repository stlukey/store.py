#!/usr/bin/env python
"""
Main application.
"""

import os

from flask import Flask

from .models import init_db_docs
from .utils import ObjectIDConverter

from .modules.products.queries import categories_get_all

class GlobalTemplateVars(object):
    def __init__(self, app):
        self.app = app

    categories = property(lambda self: categories_get_all(self.app.db))


def create_app(config=None):
    if config is None:
        config = 'production'
    print("Using '{}' config.".format(config))
    config = '../configs/{}.cfg'.format(config)


    app = Flask(__name__)
    app.config.from_pyfile(config)

    app.add_template_global(GlobalTemplateVars(app), 'global_vars')
    app.url_map.converters['ObjectID'] = ObjectIDConverter

    register_blueprints(app)
    setup_mongodb(app)



    return app


def setup_mongodb(app):
    from mongokit import Connection

    app.db = Connection(app.config['MONGODB_URI'])

    init_db_docs(app)


def register_blueprints(app):
    from .views import store as store_bp
    from .modules.products import products_bp

    app.register_blueprint(store_bp)
    app.register_blueprint(products_bp, url_prefix='/products')

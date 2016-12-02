#!/usr/bin/env python
"""
Main application.
"""

from os import path as ospath

from flask import Flask
from flask_assets import Environment
from .config import DevelopmentConfig

from .models import init_db_docs


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    register_blueprints(app)
    setup_mongodb(app)
    setup_assets(app)

    return app


def setup_mongodb(app):
    from mongokit import Connection

    app.db = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

    init_db_docs(app)


def setup_assets(app):
    app.env = Environment(app)
    app.env.load_path = [
        ospath.join(ospath.dirname(__file__), 'static/less'),
        ospath.join(ospath.dirname(__file__), 'static/coffee'),
        ospath.join(ospath.dirname(__file__), 'static/bower_components'),
    ]


def register_blueprints(app):
    from .views import store as store_bp
    from .modules.products import products_bp

    app.register_blueprint(store_bp)
    app.register_blueprint(products_bp, url_prefix='/products')

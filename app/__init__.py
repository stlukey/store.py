#!/usr/bin/env python
"""
Main application.
"""

from flask import Flask
from .config import DevelopmentConfig

from .models import init_db_docs


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    register_blueprints(app)
    setup_mongodb(app)

    return app


def setup_mongodb(app):
    from mongokit import Connection

    app.db = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

    init_db_docs(app)


def register_blueprints(app):
    from .views import store as store_bp
    from .modules.products import products_bp

    app.register_blueprint(store_bp)
    app.register_blueprint(products_bp, url_prefix='/products')

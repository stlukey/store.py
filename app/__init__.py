#!/usr/bin/env python
"""
Main application.
"""

from os import path as ospath

from flask import Flask
from flask_assets import Environment
from .config import DevelopmentConfig


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    register_blueprints(app)
    setup_mongodb(app)
    setup_assets(app)

    return app


def setup_mongodb(app):
    from mongokit import Connection
    from .store.models import to_register

    app.db = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

    for document in to_register:
        app.db.register(document)


def setup_assets(app):
    app.env = Environment(app)
    app.env.load_path = [
        ospath.join(ospath.dirname(__file__), 'sass'),
        ospath.join(ospath.dirname(__file__), 'coffee'),
        ospath.join(ospath.dirname(__file__), 'bower_components'),
    ]


def register_blueprints(app):
    from .store import store

    for bp in [store]:
        app.register_blueprint(bp)

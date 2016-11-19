#!/usr/bin/env python
"""
Main application.
"""

from flask import Flask
from .config import DevelopmentConfig

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)
    register_blueprints(app)
    mongodb(app)
    return app

def mongodb(app):
    from .store.models import to_register
    from mongokit import Connection

    conn = Connection(app.config['MONGODB_HOST'],
                      app.config['MONGODB_PORT'])

    for document in to_register:
        conn.register(document)


def register_blueprints(app):
    from .store import store

    for bp in [store]:
        app.register_blueprint(bp)


#!/usr/bin/env python
"""
Main application.
"""

from flask import Flask
from .config import BaseConfig

def create_app(config=BaseConfig):
    app = Flask(__name__)
    register_blueprints(app)
    app.config.from_object(config)
    return app

def register_blueprints(app):
    from store import store

    for bp in [store]:
        app.register_blueprint(bp)


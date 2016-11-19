"""
"""

from flask import Flask
from .store import store_bp

app = Flask(__name__)
app.register_blueprint(store_bp)


#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template

store = Blueprint('store', __name__)


@store.route('/product/<pid>')
def display_product(pid):
    return "Displaying product: {}".format(pid)


@store.route('/')
def store_front():
    return render_template('store/index.html')

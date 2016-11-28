#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, current_app, make_response
from bson.objectid import ObjectId
from pprint import pformat

store = Blueprint('store', __name__)


@store.route('/images/<product_id>/<file_name>')
def images(product_id, file_name):
    product = current_app.db.Product.get_from_id(ObjectId(product_id))
    with product.fs.get_last_version('images/{}'.format(file_name)) as f:
        response  = make_response(f.read())
    response.mimetype = 'image/jpeg'
    return response


@store.route('/product/<pid>')
def display_product(pid):
    product_id = ObjectId(pid)
    product = current_app.db.Product.get_from_id(product_id)
    categories = [c.category['name'] for c in current_app.db.ProductToCategory.find({'product._id': product_id})]
    return render_template('store/product.html', product=pformat(product, indent=4), categories=pformat(categories, indent=4))


@store.route('/')
def store_front():
    popular = []
    while len(popular) < 4:
        product = current_app.db.Product.find_random()
        if product not in popular:
            popular.append(product)

    return render_template('store/index.html', most_popular=popular)

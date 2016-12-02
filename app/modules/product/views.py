#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, current_app, make_response
from bson.objectid import ObjectId

product = Blueprint('product', __name__)


@product.route('/<product_id>/images/<file_name>')
def images(product_id, file_name):
    product = current_app.db.Product.get_from_id(ObjectId(product_id))
    with product.fs.get_last_version('images/{}'.format(file_name)) as f:
        response = make_response(f.read())
    response.mimetype = 'image/jpeg'
    return response


@product.route('/<product_id>')
@product.route('/<product_id>/<product_name>')
def view(product_id, product_name=None):
    product_id = ObjectId(product_id)
    product = current_app.db.Product.get_from_id(product_id)
    categories = list(current_app
                      .db
                      .ProductToCategory
                      .find({'product._id': product_id}))
    for i in range(len(categories)):
        categories[i] = categories[i].category['name']

    return render_template('product/product.html',
                           product=product,
                           categories=categories)

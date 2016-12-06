#!/usr/bin/env python3
"""
"""

from flask import Blueprint, current_app, make_response, render_template

from . import queries

products = Blueprint('products', __name__)



@products.route('/<ObjectID:product_id>/images/<file_name>')
def images(product_id, file_name):
    product = queries.product_get_or_abort(product_id)
    image = queries.product_get_image_or_abort(product, file_name)
    response = make_response(image)
    response.mimetype = 'image/jpeg'
    return response


@products.route('/<ObjectID:product_id>')
@products.route('/<ObjectID:product_id>/<product_name>')
def view_product(product_id, product_name=None):
    product = queries.product_get_or_abort(product_id)
    categories = queries.product_find_categories(product)

    return render_template('products/view_product.html',
                              product=product,
                              categories=list(categories))


@products.route('/<category>')
@products.route('/')
def view(category=None):
    if category:
            products = queries.product_find_by_category_or_abort(category)
    else:
        products = current_app.db.Product.find()

    return render_template('products/view.html',
                              products=products,
                              category=category)

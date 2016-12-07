#!/usr/bin/env python3
"""
"""

from flask import Blueprint, render_template, send_file

from .models import *

products = Blueprint('products', __name__)

@products.route('/<ObjectID:product_id>/images/thumbnail.jpg')
def thumbnail(product_id):
    product = Product(product_id)
    return send_file(product.thumbnail)

@products.route('/<ObjectID:product_id>')
@products.route('/<ObjectID:product_id>/<product_name>')
def view_product(product_id, product_name=None):
    product = Product(product_id)

    return render_template('products/view_product.html',
                              product=product)


@products.route('/<string:category>')
@products.route('/')
def view(category=None):
    if category:
            category = Category(category)
            products = category.products
    else:
        products = Product.find()

    return render_template('products/view.html',
                              products=products,
                              category=category)

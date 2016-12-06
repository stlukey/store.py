#!/usr/bin/env python3
"""
Data management.
"""
import os
import json
from passlib.hash import bcrypt

from . import *


@manager.command
def drop_db():
    print("Dropping database ...")
    manager.app.db.drop_database(manager.app.config['MONGODB_NAME'])


def get_products():
    product_files = ['data/' + f[:-4]
                     for f in os.listdir('data') if f.endswith('json')]
    products = []
    for product_file in product_files:
        with open(product_file + 'json') as f:
            product = json.load(f)
        product['image'] = product_file + 'jpg'
        products.append(product)

    return products


def copy_image(src, dest, length=16 * 1024):
    while True:
        buf = src.read(length)
        if not buf:
            break
        dest.write(buf)

def generate_products():
    print(' '*4 + "Generating products...")
    products = get_products()
    for product_info in products:
        print(' '*4*2 + "Adding '{}'...".format(product_info['name']))
        product = manager.app.db.Product()
        product.name = product_info['name']
        product.cost = product_info['cost']
        product.description = product_info['description']
        product.stock = product_info['stock']

        product.recipes = product_info['links']
        product.save()

        for category_name in product_info['categories']:
            category = manager.app.db.Category.one({'name': category_name})
            if category is None:
                print(' '*4*3 + "Making new category '{}'...".format(category_name))
                category = manager.app.db.Category()
                category.name = category_name
                category.save()
            product_to_category = manager.app.db.ProductToCategory()
            product_to_category.product = product
            product_to_category.category = category
            product_to_category.save()

        with open(product_info['image'], 'rb') as src:
            with product.fs.new_file(
                    'images/thumbnail.jpg'.format(product._id)
            ) as dest:
                copy_image(src, dest)

            with product.fs.new_file(
                    'images/image1.jpg'.format(product._id)
            ) as dest:
                copy_image(src, dest)

        print(' '*4*2 + "Complete!\n")
        product.save()
    print(' '*4 + "Complete!\n")

def generate_user():
    print(' '*4 + "Adding user..")
    user = manager.app.db.User()
    user.email= 'user@example.com'
    user.password = bcrypt.hash('password')
    user.first_name = 'user'
    user.last_name = 'name'

    print(' '*4*2 + "Email: " + user.email)
    print(' '*4*2 + "Password: password")

    print(' '*4 + "Complete!\n")
    user.save()

@manager.command
def create_sample():
    drop_db()
    print("Generating new database...")
    generate_products()
    generate_user()
    print("Complete!\n")


if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python3
"""
Data management.
"""
import os
import json
from flask_script import Manager
from app import create_app

app = create_app()
manager = Manager(app)


@manager.command
def drop_db():
    print("Dropping database ...")
    app.db.drop_database('store')


def get_products():
    product_files = ['data/' + f[:-4] for f in os.listdir('data') if f.endswith('json')]
    products = []
    for product_file in product_files:
        with open(product_file + 'json') as f:
            product = json.load(f)
        product['image'] = product_file + 'jpg'
        products.append(product)

    return products

def copy_image(src, dest, length=16*1024):
    while True:
        buf = src.read(length)
        if not buf:
            break
        dest.write(buf)

@manager.command
def create_sample():
    drop_db()
    print("Generating new database...")
    products = get_products()
    for product_info in products:
        product = app.db.Product()
        product.name = product_info['name']
        product.cost = product_info['cost']
        product.description = product_info['description']
        product.stock = product_info['stock']

        product.links = product_info['links']
        product.save()

        with open(product_info['image'], 'rb') as src:
            with product.fs.new_file('thumbnail') as dest:
                copy_image(src, dest)

            with product.fs.new_file('images/image1.jpg') as dest:
                copy_image(src, dest)

        print("Adding '{}'...".format(product.name))
        product.save()
    print("Complete!")

if __name__ == '__main__':
    manager.run()

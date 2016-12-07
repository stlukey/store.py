#!/usr/bin/env python3
"""
Data management.
"""
import os
import json


from app.database import conn, db
from app.modules.products.models import Product, ProductToCategory, Category
from app.modules.users.models import User

from flask_script import Manager
from app import app

manager = Manager(app)

manager.add_option('-c', '--config', dest='config', required=False)

@manager.command
def run():
    return manager.app.run(host=manager.app.config.get('HOST', 'localhost'),
                           port=manager.app.config.get('PORT', 5000))



@manager.command
def drop_db():
    print("Dropping database ...")
    conn.drop_database(os.environ.get('MONGODB_NAME', 'online-store'))


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




def generate_products():
    print(' '*4 + "Generating products...")
    products = get_products()
    for product_info in products:
        print(' '*4*2 + "Adding '{}'...".format(product_info['name']))
        product = Product.new(
            name=product_info['name'],
            cost=product_info['cost'],
            description=product_info['description'],
            stock=product_info['stock'],
            recipes=product_info['links']
        )

        for category_name in product_info['categories']:
            category = Category.find_by_name(category_name)
            if not category.exists:
                print(' '*4*3 + "Making new category '{}'...".format(category_name))
                category = Category.new(
                    name=category_name
                )
            ProductToCategory.new(
                product=product,
                category=category
            )

        with open(product_info['image'], 'rb') as src:
            product.thumbnail = src.read()

        print(' '*4*2 + "Complete!\n")

    print(' '*4 + "Complete!\n")

def generate_user():
    print(' '*4 + "Adding user..")
    user = User.new(
        _id= 'user@example.com',
        password = 'password',
        first_name = 'user',
        last_name = 'name'
    )

    print(' '*4*2 + "Email: " + user['_id'])
    print(' '*4*2 + "Password: password")

    print(' '*4 + "Complete!\n")

@manager.command
def create_sample():
    drop_db()
    print("Generating new database...")
    generate_products()
    generate_user()
    print("Complete!\n")


if __name__ == '__main__':
    manager.run()

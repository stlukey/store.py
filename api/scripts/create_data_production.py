#!/usr/bin/env python3
"""
Data management.
"""
import os
import json

from ..database import client
from ..resources.products.models import Product, ProductToCategory, Category
from ..resources.images.models import Image, SetImage
from ..resources.users.models import User
from ..resources.pages.models import Page


def drop_db():
    print("Dropping database ...")
    client.drop_database(os.environ.get('MONGODB_NAME', 'online-store'))


def get_products():
    product_files = ['data/' + f[:-4]
                     for f in os.listdir('data') if f.endswith('json')]
    products = []
    for product_file in product_files:
        with open(product_file + 'json') as f:
            product = json.load(f)
        with open(product_file + 'jpg', 'rb') as f:
            image = Image.new(f)
        product['image'] = image.url
        products.append(product)

    return products

def add_set_images():
    print(' ' * 4 + "Adding set images...")

    print(' ' * 4 * 2 + "Adding home.jpg...")
    with open('data/home.jpg', 'rb') as f:
        image = Image.new(f)
    SetImage.new(_id='home', image=str(image._id))

    print(' ' * 4 * 2 + "Adding background.jpg...")
    with open('data/background.jpg', 'rb') as f:
        image = Image.new(f)
    SetImage.new(_id='background', image=str(image._id))

    print(' ' * 4 * 2 + "Adding favicon.jpg...")
    with open('data/favicon.jpg', 'rb') as f:
        image = Image.new(f)
    SetImage.new(_id='favicon', image=str(image._id))

    print(' ' * 4 + "Complete!\n")


def generate_pages():
    print(' ' * 4 + "Generating pages...")

    print(' ' * 4 * 2 + "Adding contact page...")
    Page.new(_id='contact', content='<h1>Contact</h1>')

    print(' ' * 4 * 2 + "Adding about page...")
    Page.new(_id='about', content='<h1>About</h1>')

    print(' ' * 4 * 2 + "Adding press page...")
    Page.new(_id='press', content='<h1>Press</h1>')

    print(' ' * 4 * 2 + "Adding faqs page...")
    Page.new(_id='faqs', content='<h1>FAQs</h1>')

    print(' ' * 4 * 2 + "Adding delivery-and-returns page...")
    Page.new(_id='delivery-and-returns', content='<h1>Delivery and Returns</h1>')

    print(' ' * 4 * 2 + "Adding terms-and-conditions page...")
    Page.new(_id='terms-and-conditions', content='<h1>Terms and Conditions</h1>')

    print(' ' * 4 * 2 + "Adding privacy page...")
    Page.new(_id='privacy', content='<h1>Privacy</h1>')

    print(' ' * 4 + "Complete!\n")


def generate_products():
    print(' ' * 4 + "Generating products...")
    products = get_products()
    for product_info in products:
        print(' ' * 4 * 2 + "Adding '{}'...".format(product_info['name']))
        product = Product.new(
            name=product_info['name'],
            cost=product_info['cost'],
            description=product_info['description'],
            stock=product_info['stock'],
            recipes=product_info['links'],
            measurements=product_info['measurements']
        )

        for category_name in product_info['categories']:
            category = Category.find_by_name(category_name)
            if not category.exists:
                print(
                    ' ' * 4 * 3 +
                    "Making new category '{}'...".format(category_name))
                category = Category.new(
                    name=category_name
                )
            ProductToCategory.new(
                product=product,
                category=category
            )

        product.update(dict(active=True, images=[product_info['image']]))

        print(' ' * 4 * 2 + "Complete!\n")

    print(' ' * 4 + "Complete!\n")


def generate_user():
    print(' ' * 4 + "Adding user..")
    user = User.new(
        _id='user@example.com',
        password='password',
        first_name='user',
        last_name='name',
        admin=False,
        active=True
    )

    print(' ' * 4 * 2 + "Email: " + user.id)
    print(' ' * 4 * 2 + "Password: password")

    print(' ' * 4 + "Complete!\n")

def generate_admin():
    print(' ' * 4 + "Adding admin..")
    user = User.new(
        _id='sinamaryam@gmail.com',
        password='password',
        first_name='admin',
        last_name='',
        admin=True,
        active=True
    )

    print(' ' * 4 * 2 + "Email: " + user.id)
    print(' ' * 4 * 2 + "Password: password")

    print(' ' * 4 + "Complete!\n")


def create_sample():
    drop_db()
    print("Generating new database...")
    add_set_images()
    generate_products()
    generate_pages()
    #generate_user()
    generate_admin()
    print("Complete!\n")


if __name__ == '__main__':
    create_sample()

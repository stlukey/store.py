from flask import Blueprint

users = Blueprint('users', __name__)

@users.route('/login', methods=['GET', 'POST'])
def login():
    pass




from flask import current_app
from bson.objectid import ObjectId
from flask_login import login_user
from passlib.hash import bcrypt

class User(object):
    def __init__(self, user_id):
        self.id = ObjectId(user_id)
        self.doc = current_app.db.User.get_from_id(self.id)

    @property
    def is_authenticated(self):
        return bool(self.doc)

    @property
    def is_active(self):
        return self.doc and self.doc.active

    @property
    def is_anonymous(self):
        return not self.doc

    def get_id(self):
        return str(self.id)

    @classmethod
    def login(cls, email, password):
        user = current_app.db.User.find_one({'email': email})
        if user:
            if bcrypt.verify(password, user.password):
                user = User(user._id)
                login_user(user)
            else:
                user = None
        return user



def load_user(user_id):
    return User(user_id)

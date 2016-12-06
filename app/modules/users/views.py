from urllib.parse import urlparse, urljoin
from flask import Blueprint, request, render_template, flash, abort, redirect, url_for, current_app
from flask_login import login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from passlib.hash import bcrypt

from .user import User

users = Blueprint('users', __name__)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class RegistrationForm(LoginForm):
    first_name = StringField('First name', [DataRequired()])
    last_name = StringField('First name', [DataRequired()])

    contact_num = StringField('Contact number', [DataRequired()])


@users.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if not login_form.validate_on_submit():
        return render_template('users/login.html', title="Login",
                               login_form=login_form, registration_form=registration_form)

    email = request.form['email']
    password = request.form['password']
    user = User.login(email, password)

    if not user:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('users.login'))

    flash('Logged in successfully.', 'success')

    next = request.args.get('next')
    if not is_safe_url(next):
        return redirect(url_for('store.index'))


    return redirect(next or url_for('store.index'))


@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')

    next = request.args.get('next')
    if not is_safe_url(next):
        return abort(400)

    return redirect(next or url_for('store.index'))

@users.route("/register", methods=['POST'])
def register():
    form = RegistraionForm()

    if not form.validate_on_submit():
        flash("Invalid details.", 'danger')
        return redirect(url_for('users.login'))

    email = request.form['email']
    if current_app.db.User.find_one({'email': email}):
        flash('An account for that email address already exists.', 'danger')
        return redirect(url_for('users.login'))

    user = current_app.db.User()
    user.email = email
    user.password = bcrypt.hash(request.form['password'])
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.contact_num = request.form['contact_num']
    user.save()

    flash('Account Created.', 'success')
    return redirect(url_for('users.login'))



import os

DEBUG=bool(int(os.environ['FLASK_DEBUG']))
TESTING=bool(int(os.environ['FLASK_TESTING']))
SECRET_KEY=os.environ['FLASK_SECRET']
SECURITY_SALT = os.environ['SECURITY_SALT']

# email server
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

SERVER_EMAIL = "no-reply@maryamspersianpantry.com"

JS_ORIGIN = os.environ.get('JS_ORIGIN') + "/demo"

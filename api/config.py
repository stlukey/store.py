import os

DEBUG=bool(int(os.environ['FLASK_DEBUG']))
TESTING=bool(int(os.environ['FLASK_TESTING']))
SECRET_KEY=os.environ['FLASK_SECRET']

# email server
MAIL_SERVER = os.environ.get('MAILGUN_SMTP_SERVER')
MAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT')
MAIL_USE_TLS = bool(int(os.environ.get('MAIL_USE_TLS')))
MAIL_USE_SSL = bool(int(os.environ.get('MAIL_USE_SSL')))
MAIL_USERNAME = os.environ.get('MAILGUN_SMTP_LOGIN')
MAIL_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')

SERVER_EMAIL = "no-reply@maryamsingredients.mailgun.com"

JS_ORIGIN = os.environ.get('JS_ORIGIN')

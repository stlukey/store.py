from flask import render_template
from flask_mail import Message

from .config import SERVER_EMAIL
from .utils import async

@async
def send_email(subject, recipients, text_body):
    from . import mail
    msg = Message(subject, sender=SERVER_EMAIL, recipients=recipients)

    msg.body = text_body
    #msg.html = html_body
    mail.send(msg)

def order_confirmation(user, order):
    send_email("Order Confirmation",
               [user.id],
               render_template("order-confirmation.txt",
                               user=user, order=order))

def order_dispatched(user, order):
    send_email("Order Dispatched",
               [user.id],
               render_template("order-dispatched.txt",
                               user=user, order=order))

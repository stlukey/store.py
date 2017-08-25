#!/usr/bin/env python3
"""
Activate users
"""
import sys

from ..resources.users.models import User


def activate_user(email):
    print(' ' * 4 + "Activating user..")
    user = User(email)
    user.update({'active': True})
    print(' ' * 4 * 2 + "Email: " + user.id)
    print(' ' * 4 + "Complete!\n")


if __name__ == '__main__':
    activate_user(sys.argv[1])

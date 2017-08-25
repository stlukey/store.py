#!/usr/bin/env python3
"""
Add admins.
"""
import sys

from ..resources.users.models import User


def make_admin(email):
    print(' ' * 4 + "Adding admin..")
    user = User(email)
    user.update({'admin': True})
    print(' ' * 4 * 2 + "Email: " + user.id)
    print(' ' * 4 + "Complete!\n")


if __name__ == '__main__':
    make_admin(sys.argv[1])

#!/usr/bin/env python
"""
Manage script.
"""

from flask_script import Manager
from app import app

from sh import pip, ErrorReturnCode

manager = Manager(app)

@manager.command
def freeze():
    """Freeze python packages.
    """
    print("Freezing packages...")

    try:
        pip('freeze', _out="requirements.txt")
    except ErrorReturnCode:
        return print("Failure! There was an error.")

    print("Success!")



if __name__ == '__main__':
    manager.run()


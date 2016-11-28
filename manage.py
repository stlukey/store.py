#!/usr/bin/env python3
"""
Manage script.
"""

from flask_script import Manager
from app import create_app

from sh import pip, git, ErrorReturnCode

app = create_app()
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


def commit_install(package):
    print("Commiting changes to requirements.txt ...")
    msg = "Added '{}' to requirements.txt".format(package)

    try:
        git('commit requirements.txt', '-m', msg, _out=print)
    except:
        return print("Failure! There was an error.")

    print("Success")


@manager.command
def install(package):
    """Installs package, freezes and commits.
    """
    print("Installing '{}'...".format(package))

    try:
        pip('install', package, _out=print)
    except:
        return print("Failure! There was an error.!")

    print("Success!")
    freeze()
    commit_install(package)


@manager.command
def run(ip='127.0.0.1', port=5000):
    current_app = app
    if False:
        # TODO: Apply Production config.
        current_app != app
    app.run(host=ip, port=int(port))

if __name__ == '__main__':
    manager.run()

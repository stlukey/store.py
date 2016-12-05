from flask_script import Manager
from app import create_app

manager = Manager(create_app)

manager.add_option('-c', '--config', dest='config', required=False)

@manager.command
def run():
    return manager.app.run(host=manager.app.config.get('HOST', 'localhost'),
                           port=manager.app.config.get('PORT', 5000))


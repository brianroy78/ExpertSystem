from configparser import ConfigParser

from controllers.controllers import main_blueprint
from controllers.engine_controllers import engine_blueprint
from database import set_settings
from flask import Flask
from flask_cors import CORS

application = Flask(__name__, template_folder="./templates")

CORS(application)

config = ConfigParser()
config.read('settings.ini')
set_settings(config['DEFAULT']['sqlalchemy.url'])

application.register_blueprint(main_blueprint)
application.register_blueprint(engine_blueprint)

application.run()

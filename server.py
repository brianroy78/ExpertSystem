from configparser import ConfigParser

from controllers.controllers import main_blueprint
from database import set_settings
from flask import Flask
from flask_cors import CORS

application = Flask(__name__, template_folder="./templates")

CORS(application)

config = ConfigParser()
config.read('settings.ini')
set_settings(config['DEFAULT']['sqlalchemy.url'])

application.register_blueprint(main_blueprint)

application.run()

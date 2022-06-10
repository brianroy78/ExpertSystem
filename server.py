from configparser import ConfigParser

from database import set_settings, Data
from flask import Flask
from database import Base
from database.tables import *

app = Flask(__name__, template_folder="./templates")

config = ConfigParser()
config.read('settings.ini')
set_settings(config['DEFAULT']['sqlalchemy.url'])

Base.metadata.create_all(Data.ENGINE)

app.run()

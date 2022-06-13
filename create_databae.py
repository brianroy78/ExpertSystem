from configparser import ConfigParser

from database import Base, set_settings, Data
from database.tables import *

config = ConfigParser()
config.read('settings.ini')
set_settings(config['DEFAULT']['sqlalchemy.url'])

Base.metadata.create_all(Data.ENGINE)

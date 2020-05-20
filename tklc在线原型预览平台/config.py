import os,random,sys
from datetime import timedelta
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY =  os.environ.get('SECRET_KEY') or str(random.random())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)

class DevConfig(Config):
    DEBUG=True
    if sys.platform.startswith('win'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'devdb.db')
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:////'+os.path.join(basedir,'devdb.db')

class ProdConfig(Config):
    DEBUG=False


config={
    "development":DevConfig,
    "production":ProdConfig,
    "default":DevConfig,
}

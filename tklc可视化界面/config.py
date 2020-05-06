import os,random
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY =  os.environ.get('SECRET_KEY') or str(random.random())
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    DEBUG=True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:////'+os.path.join(basedir,'devdb.db')

class ProdConfig(Config):
    DEBUG=False



config={
    "development":DevConfig,
    "production":ProdConfig,
    "default":DevConfig,
}

from flask import Flask,Blueprint
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config,DevConfig

# bootstrap初始化
bootstrap = Bootstrap()
db = SQLAlchemy()

# BluePrint初始化
tklc = Blueprint('tklc',__name__,template_folder='templates',static_folder='static')

def tklc_init(cfg_name):
    app = Flask(__name__)
    app.config.from_object(config[cfg_name])
    bootstrap.init_app(app)
    db.init_app(app)
    app.register_blueprint(tklc)
    return app

from tklc import views

__author__ = 'dkasyanov'
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


__name__ = 'confiskat'
app = Flask(__name__)
app.config.from_object('config')
app.config['MONGOALCHEMY_DATABASE'] = 'confiskat2'
db = SQLAlchemy(app)


from app import views
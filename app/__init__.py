__author__ = 'dkasyanov'
from flask import Flask
from flask.ext.mongoalchemy import MongoAlchemy


#__name__ = 'confiskat'
app = Flask(__name__)
app.config.from_object('config')
app.config['MONGOALCHEMY_DATABASE'] = 'confiskat2'
db = MongoAlchemy(app)


from app import views
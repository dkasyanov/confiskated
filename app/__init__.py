__author__ = 'dkasyanov'
from flask import Flask, _app_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(bind=engine), scopefunc=_app_ctx_stack.__ident_func__)


from app import views
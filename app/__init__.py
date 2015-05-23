__author__ = 'dkasyanov'
from flask import Flask, _app_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI, ADMINS, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER, MAIL_USERNAME, basedir
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

engine = create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(bind=engine), scopefunc=_app_ctx_stack.__ident_func__)

from app import views

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'confiscated failure', credentials, ())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    file_handler = RotatingFileHandler(os.path.join(basedir, 'tmp/error.log'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('confiscated startup')
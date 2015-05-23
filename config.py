__author__ = 'dkasyanov'
import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

LOTS_PER_PAGE = 10

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


#mail server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'korvin.work@gmail.com'
MAIL_PASSWORD = '5cdt8ryihjz3'

# adminitstrator list
ADMINS = ['korvin1986@gmail.com']
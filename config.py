__author__ = 'dkasyanov'
import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

LOTS_PER_PAGE = 10

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
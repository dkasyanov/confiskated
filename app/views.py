# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import app, db
from flask import render_template
from forms import FiltersForm
from config import LOTS_PER_PAGE
from models import Lot, Address


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>', methods=['POST', 'GET'])
def index(page=1):
    lots = Lot.query.filter().paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    return render_template('base.html',
                           lots=lots)

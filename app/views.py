# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import app, db
from flask import render_template, redirect, url_for, request, g, session, jsonify
from forms import FiltersForm
from config import LOTS_PER_PAGE
from models import Lot, Address, Type, Region, Country, City, Square
import json


@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
@app.route('/index/<int:page>', methods=['POST', 'GET'])
def index(page=1):
    session['form_filter'] = None
    form = FiltersForm()
    regions = [(u'0', u'Вся Украина')]
    cities = [(u'0', u'Все города')]
    types = [(u'0', u'Все категории')]

    regions.extend(sorted([(i.id, i.name) for i in Region.query.all()], key=lambda x: x[1]))
    types.extend([(i.id, i.name) for i in Type.query.all()])

    form.regionSelector.choices = regions
    form.citySelector.choices = cities
    form.typeSelector.choices = types
    lots = Lot.query
    if form.is_submitted():
        filter_action(form)
        return redirect(url_for('filter'))

    lots = sort_lots(lots).paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    return render_template('index.html',
                           lots=lots,
                           form=form)


@app.route('/filter', methods=['GET', 'POST'])
@app.route('/filter/<int:page>', methods=['GET', 'POST'])
def filter(page=1):
    data = json.loads(session['form_filter'])
    form = FiltersForm()
    if form.is_submitted():
        filter_action(form)
        return redirect(url_for('filter', page=page))

    regions = [(u'0', u'Вся Украина')]
    cities = [(u'0', u'Все города')]
    types = [(u'0', u'Все категории')]

    regions.extend(sorted([(i.id, i.name) for i in Region.query.all()], key=lambda x: x[1]))
    types.extend([(i.id, i.name) for i in Type.query.all()])

    form.regionSelector.choices = regions
    form.citySelector.choices = cities
    form.typeSelector.choices = types
    lots = Lot.query
    if data.get('r'):
        lots = lots.join(Address).filter(Address.region_id == int(data.get('r')))
        form.regionSelector.default = int(data.get('r'))
        if int(data.get('r')) > 0:
            cities.extend(sorted([(i.id, i.name) for i in City.query.filter_by(region_id=int(data.get('r'))).all()]))
            form.citySelector.choices = cities
    if data.get('c'):
        lots = lots.filter(Address.city_id == int(data.get('c')))
        form.citySelector.default = int(data.get('c'))
    if data.get('t'):
        lots = lots.join(Type).filter(Type.id == int(data.get('t')))
        form.typeSelector.default = int(data.get('t'))
    if data.get('pf'):
        lots = lots.filter(Lot.price >= int(data.get('pf')))
        form.price_from.default = int(data.get('pf'))
    if data.get('pt'):
        lots = lots.filter(Lot.price <= int(data.get('pt')))
        form.price_to.default = int(data.get('pt'))
    if data.get('sf'):
        lots = lots.join(Square).filter(Square.common >= float(data.get('sf')))
        form.square_from.default = float(data.get('sf'))
    if data.get('st'):
        lots = lots.join(Square).filter(Square.common <= float(data.get('st')))
        form.square_to.default = float(data.get('st'))
    if data.get('rr'):
        rr = [x+1 for x in range(0, 4) if data.get('rr')[x] == '1']
        q = Lot.rooms.in_(rr)
        if 4 in rr:
            q = q.__or__(Lot.rooms > 4)
        lots = lots.filter(q)
        form.room1.default = 1 if 1 in rr else 0
        form.room2.default = 2 if 2 in rr else 0
        form.room3.default = 3 if 3 in rr else 0
        form.room4.default = 4 if 4 in rr else 0

    lots = sort_lots(lots).paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    form.process()
    return render_template('filter.html',
                           lots=lots,
                           form=form)


@app.route('/get_cities', methods=['POST'])
def get_cities():
    cities = sorted([(i.name, i.id) for i in City.query.filter_by(region_id=int(request.form['region'])).order_by(City.name).all()])
    return jsonify(cities)


@app.route('/sort_by', methods=['POST'])
def sort_by():
    session['sort_type'] = request.form['sort_type']
    session['direction'] = request.form['sort_dir']
    return jsonify([])


def sort_lots(lots):
    if session.get('sort_type', None) == 'price':
        if session['direction'] == 'asc':
            lots = lots.order_by(Lot.price)
        else:
            lots = lots.order_by(Lot.price.desc())
    elif session.get('sort_type', None) == 'date':
        if session['direction'] == 'asc':
            lots = lots.order_by(Lot.date)
        else:
            lots = lots.order_by(Lot.date.desc())
    return lots


def filter_action(form):
    region_id = (int(form.regionSelector.data) if int(form.regionSelector.data) > 0 else None)
    city_id = (int(form.citySelector.data) if int(form.citySelector.data) > 0 else None)
    type_id = (int(form.typeSelector.data) if int(form.typeSelector.data) > 0 else None)
    room = {'1': form.room1.data, '2': form.room2.data, '3': form.room3.data, '4': form.room4.data}
    price_from = form.price_from.data
    price_to = form.price_to.data
    square_from = form.square_from.data
    square_to = form.square_to.data
    rr = ''
    for i in sorted(room.keys()):
        rr += str(int(room[i]))
    if rr == '0000':
        rr = None

    form_filter = {'r': region_id, 'c': city_id, 't': type_id,
                   'pf': price_from, 'pt': price_to,
                   'sf': square_from, 'st': square_to,
                   'rr': rr}
    session['form_filter'] = json.dumps(form_filter)
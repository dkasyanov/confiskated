# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import app, db
from flask import render_template, redirect, url_for, request, g, session, jsonify
from forms import FiltersForm
from config import LOTS_PER_PAGE
from models import Lot, Address, Type, Region, Stats, City, Square, Bank
import json
from datetime import datetime
import flot


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@app.route(u'/index/<int:page>', methods=['POST', 'GET'])
def index(page=1):
    sort = request.args.get('sort', None)
    write_stats(request)
    form = FiltersForm()
    regions = [(u'0', u'Вся Украина')]
    cities = [(u'0', u'Все города')]
    types = [(u'0', u'Все категории')]
    banks = [(u'0', u'Все банки')]

    regions.extend(sorted([(i.id, i.name) for i in Region.query.all()], key=lambda x: x[1]))
    types.extend([(i.id, i.name) for i in Type.query.all()])
    banks.extend([(i.id, i.name) for i in Bank.query.all()])

    form.regionSelector.choices = regions
    form.citySelector.choices = cities
    form.typeSelector.choices = types
    form.bankSelector.choices = banks

    lots = Lot.query
    if form.is_submitted():
        filter_action(form)
        return redirect(url_for('filter'))

    if sort == 'asc':
        lots = lots.order_by(Lot.price)
    elif sort == 'desc':
        lots = lots.order_by(Lot.price.desc())

    lots = lots.paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    return render_template('index.html',
                           lots=lots,
                           form=form,
                           sort=sort)


@app.route('/filter', methods=['GET', 'POST'])
@app.route('/filter/<int:page>', methods=['GET', 'POST'])
def filter(page=1):
    sort = request.args.get('sort', None)
    write_stats(request)
    data = json.loads(session['form_filter'])
    form = FiltersForm()
    if form.is_submitted():
        filter_action(form)
        return redirect(url_for('filter', page=page))

    regions = [(u'0', u'Вся Украина')]
    cities = [(u'0', u'Все города')]
    types = [(u'0', u'Все категории')]
    banks = [(u'0', u'Все банки')]

    regions.extend(sorted([(i.id, i.name) for i in Region.query.all()], key=lambda x: x[1]))
    types.extend([(i.id, i.name) for i in Type.query.all()])
    banks.extend([(i.id, i.name) for i in Bank.query.all()])

    form.regionSelector.choices = regions
    form.citySelector.choices = cities
    form.typeSelector.choices = types
    form.bankSelector.choices = banks
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
    if data.get('b'):
        lots = lots.join(Bank).filter(Bank.id == int(data.get('b')))
        form.bankSelector.default = int(data.get('b'))
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

    if sort == 'asc':
        lots = lots.order_by(Lot.price)
    elif sort == 'desc':
        lots = lots.order_by(Lot.price.desc())

    lots = lots.paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    form.process()
    return render_template('filter.html',
                           lots=lots,
                           form=form,
                           sort=sort)


@app.route('/get_cities', methods=['POST'])
def get_cities():
    cities = sorted([(i.name, i.id) for i in City.query.filter_by(region_id=int(request.form['region'])).order_by(City.name).all()])
    return jsonify(cities)


@app.route('/statistics')
def statistics():
    dates = Stats.query.group_by(Stats.date).limit(7).all()
    unique_users = []
    for date in dates:
        unique_users.append((date.date.strftime("%B %d, %Y"), Stats.query.filter_by(date=date.date).group_by(Stats.ip).count()))
    if not unique_users:
        unique_users = [(datetime.utcnow().date().strftime("%B %d, %Y"), 0)]

    series = flot.Series(unique_users)
    visits_graph = flot.Graph([series, ])
    return render_template('statistics.html', data=visits_graph)


def filter_action(form):
    region_id = (int(form.regionSelector.data) if int(form.regionSelector.data) > 0 else None)
    city_id = (int(form.citySelector.data) if int(form.citySelector.data) > 0 else None)
    type_id = (int(form.typeSelector.data) if int(form.typeSelector.data) > 0 else None)
    bank_id = (int(form.bankSelector.data) if int(form.bankSelector.data) > 0 else None)
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

    form_filter = {'r': region_id, 'c': city_id, 't': type_id, 'b': bank_id,
                   'pf': price_from, 'pt': price_to,
                   'sf': square_from, 'st': square_to,
                   'rr': rr}
    session['form_filter'] = json.dumps(form_filter)


def write_stats(request):
    stats = Stats()
    agent = request.user_agent
    stats.agent_platform = agent.platform
    stats.agent_browser = agent.browser
    stats.agent_browser_version = agent.version
    stats.agent_lang = agent.language
    
    trusted_proxies = {'127.0.0.1', '10.9.180.95'}  # define your own set
    route = request.access_route + [request.remote_addr]
    remote_addr = next((addr for addr in reversed(route)
                        if addr not in trusted_proxies), request.remote_addr)
    
    stats.ip = remote_addr
    stats.referrer = request.referrer
    stats.time = datetime.utcnow().time()
    stats.date = datetime.utcnow().date()
    db.session.add(stats)
    db.session.commit()
# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import app, db
from flask import render_template, redirect, url_for
from forms import FiltersForm
from config import LOTS_PER_PAGE
from models import Lot, Address


@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
@app.route('/index/<int:page>', methods=['POST', 'GET'])
@app.route('/index?q=<string:query>', methods=['GET', 'POST'])
def index(page=1, query=None):
    form = FiltersForm()
    regions = [(u'Вся Украина', u'Вся Украина')]
    cities = [(u'Все города', u'Все города')]
    types = [(u'Все категории', u'Все категории')]

    regions.extend(sorted([(i, i) for i in Lot.query.distinct(Lot.address.region)]))
    cities.extend(sorted(set([(i, i) for i in Lot.query.filter(Lot.address.region == u'Донецкая область').distinct(Lot.address.city)])))
    types.extend([(i, i) for i in Lot.query.distinct(Lot.type)])

    form.regionSelector.choices = regions
    form.citySelector.choices = cities
    form.typeSelector.choices = types
    lots = Lot.query
    if form.is_submitted():
        query = '?q='
        region = form.regionSelector.data
        city = form.citySelector.data
        type = form.typeSelector.data
        room = {'1': form.room1.data, '2': form.room2.data, '3': form.room3.data, '4': form.room4.data}
        price_from = form.price_from.data
        price_to = form.price_to.data
        square_from = form.square_from.data
        square_to = form.square_to.data

        if region != u'Вся Украина':
            lots = lots.filter(Lot.address.region == region)
            query += 'r='+region+'&'
        if city != u'Все города':
            lots = lots.filter(Lot.address.city == city)
            query += 'c='+city+'&'
        if type != u'Все категории':
            lots = lots.filter(Lot.type == type)
            query += 't='+type+'&'
        if True in room.values():
            q = Lot.rooms
            r = []
            for i in room.keys():
                if room[i]:
                    r.append(int(i))
            q = q.in_(*r)
            if room['4']:
                q = q.or_(Lot.rooms.gt_(4))
            lots = lots.filter(q)
        if price_from:
            lots = lots.filter(Lot.price.ge_(price_from))
        if price_to:
            lots = lots.filter(Lot.price.le_(price_to))
        if square_from:
            lots = lots.filter(Lot.square.common.ge_(square_from))
        if square_to:
            lots = lots.filter(Lot.square.common.le_(square_to))

        return redirect(url_for('index'), query)
    elif query:
        q_data = {}


    lots = lots.paginate(page, per_page=LOTS_PER_PAGE, error_out=True)
    return render_template('base.html',
                           lots=lots,
                           form=form)

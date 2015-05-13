# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'


import Queue
import threading
import time
import real_estate
import planetestate
from app.models import Lot
from app import db_session
from datetime import datetime
from app.db_lib import *

queue = Queue.Queue()
LOCK = threading.RLock()
global updated
global added
updated = 0
added = 0


def worker():
    global queue
    while True:
        try:
            data = queue.get_nowait()
        except Queue.Empty, error:
            print error
            return

        link, region, city, bank = data
        lot_parsed = None
        bank_obj = None
        if bank == u'ПУМБ':
            LOCK.acquire()
            bank_obj = real_estate.get_bank()
            LOCK.release()
            lot_parsed = real_estate.parse_lot(link, region, city)
        elif bank == u'ПриватБанк':
            LOCK.acquire()
            bank_obj = planetestate.get_bank()
            LOCK.release()
            lot_parsed = planetestate.parse_lot(link)

        if lot_parsed:
            write_to_db(lot_parsed, region, city, bank_obj)
        else:
            queue.put(data)


def write_to_db(lot, region, city, bank_obj):
    global added
    global updated
    LOCK.acquire()
    session = db_session()
    lot_parsed = Lot()
    lot_parsed.source_id = lot.get('source_id')
    lot_parsed.link = lot.get('link')
    lot_parsed.type = get_type(lot.get('type'))
    country = get_country(lot.get('country'))
    if lot.get('region'):
        region = get_region(lot.get('region'), country)
    else:
        region = get_region(region, country)
    session.add(region)
    if lot.get('city'):
        city = get_city(lot.get('city'), region)
    else:
        city = get_city(city, region)
    session.add(city)
    lot_parsed.address = get_address(country, region, city, lot.get('street'), lot.get('other'))
    squares = Square()
    session.add(squares)
    squares.bathroom = lot.get('bathroom')
    squares.common = lot.get('common')
    squares.kitchen = lot.get('kitchen')
    squares.living = lot.get('living')
    squares.territory = lot.get('territory')
    squares.toilet = lot.get('toilet')
    squares.wc = lot.get('wc')
    lot_parsed.square = get_square(squares)
    lot_parsed.communications = lot.get('communications')
    lot_parsed.rooms = lot.get('rooms')
    lot_parsed.level = lot.get('level')
    lot_parsed.build_year = lot.get('build_year')
    lot_parsed.description = lot.get('description')
    lot_parsed.photo = lot.get('photo')
    lot_parsed.price = lot.get('price')
    lot_parsed.price_credit = lot.get('price_credit')
    lot_parsed.price_rent = lot.get('price_rent')
    lot_parsed.date = datetime.utcnow()
    lot_parsed.source = lot.get('source')
    lot_parsed.bank = bank_obj

    lot_db = session.query(Lot).filter_by(source_id=lot_parsed.source_id, source=lot_parsed.source).first()
    curr_date = datetime.utcnow()

    if lot_db:
        # print "lot %d updated" % lot_db.source_id
        lot_db.date = curr_date
        session.merge(lot_db)
        session.commit()
        updated += 1
    else:
        # print "lot %d added to db" % lot.source_id
        lot_parsed.date = curr_date
        session.add(lot_parsed)
        session.commit()
        added += 1
    session.close()
    LOCK.release()


def main():
    start = time.time()
    print "STARTED"
    links = planetestate.get_lots_links()
    links.extend(real_estate.get_lots_links())
    finish = time.time()
    print 'Lot links parsed, time: %.2f seconds, total: %d links' % (finish-start, len(links))
    start = time.time()
    for link in links:
        queue.put(link)

    for _ in xrange(12):
        thread_ = threading.Thread(target=worker)
        thread_.start()

    while threading.active_count() > 1:
        time.sleep(1)
    finish = time.time()
    print "FINISHED"
    print 'Execution of all threads is complete, time: %.2f seconds' % (finish-start)
    print "Added: " + str(added) + "\nUpdated: " + str(updated)


if __name__ == "__main__":
    main()
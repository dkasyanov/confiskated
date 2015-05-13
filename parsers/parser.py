# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

import thread
import time
from datetime import datetime
import planetestate
import real_estate
from app.models import Lot
from app import db

start = time.time()

global updated
global added
updated = 0
added = 0
links = []
links.extend(planetestate.get_lots_links())
#links.extend(real_estate.get_lots_links())

# from app.models import Bank
# import app.db_lib
# bank_obj = Bank()
# bank_obj.name = u'ПриватБанк'
# bank_obj.website = u'http://privatbank.ua'
# bank_obj.logo = u'https://privatbank.ua/img/logo.png'
# bank_obj = app.db_lib.get_or_create_bank(bank_obj)
# links.extend([(u'http://planetestate.com.ua/estate/7434', None, None, bank_obj), (u'http://planetestate.com.ua/estate/7987', None, None, bank_obj)])
global lots
lots = []


def parse_data(link, bank, lock, region=None, city=None):
    global updated
    global added
    if bank.name == u'ПУМБ':
        lot_parsed = real_estate.parse_lot(link, region, city)
    elif bank.name == u'ПриватБанк':
        lot_parsed = planetestate.parse_lot(link, bank)
    if not lot_parsed:
        return
    curr_date = datetime.utcnow()
    lots.append(lot_parsed)
    #lot_db = Lot.query.filter_by(source_id=lot_parsed.source_id, source=lot_parsed.source).first()
    # if lot_parsed.compare(lot_db):
    #     print "lot %d updated" % lot_db.source_id
    #     lot_db.date = curr_date
    #     db.session.merge(lot_db)
    #     db.session.commit()
    #     updated += 1
    # else:
    #     print "lot %d added to db" % lot_parsed.source_id
    #     lot_parsed.date = curr_date
    #     db.session.add(lot_parsed)
    #     db.session.commit()
    #     added += 1
    # Освобождаем объект
    lock.release()

# Список объектов блокировки потоков
lock_list = []
for lot, region, city, bank_obj in links:
    # Создаем новый объект блокировки. Изначально блокировка в состоянии False.
    lock = thread.allocate_lock()
    # Блокируем объект
    lock.acquire()
    # Запоминаем блокировку
    lock_list.append(lock)
    # Запускаем новый поток и выполняем в нем функцию
    thread.start_new_thread(parse_data, (lot, bank_obj, lock, region, city))

# Ожидаем завершения всех потоков
while(any([l.locked() for l in lock_list])):
    time.sleep(5)


finish = time.time()
print len(lots)
print 'Execution of all threads is complete, time: %.2f' % (finish-start)
print "Added: " + str(added) + "\nUpdated: " + str(updated)
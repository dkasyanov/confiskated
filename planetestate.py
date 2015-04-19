# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

import requests
import lxml.html
from app.models import Lot, Address, Square, Communication
from datetime import datetime
from app import db


base_url = "http://planetestate.com.ua/estate/sell"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
}
SOURCE = 'www.planetestate.com.ua'


def is_last_page(data):
    doc = lxml.html.document_fromstring(data)
    if doc.body.cssselect('.paging>a')[-1].text == u"→":
        return False
    return True


def get_lots_links():
    page_url_template = "http://planetestate.com.ua/?perpage=24&category=sell&page=%d"
    page_index = 1
    data = list()

    r = requests.get((page_url_template % page_index), headers=headers)
    r.encoding = "UTF-8"
    document = lxml.html.document_fromstring(r.text)
    document.make_links_absolute(base_url)
    objects = document.body.cssselect('.obj')
    for obj in objects:
        data.append(obj.cssselect('.img')[0].get('href'))

    while not is_last_page(r.text):
        page_index += 1
        r = requests.get((page_url_template % page_index), headers=headers)
        r.encoding = "UTF-8"
        document = lxml.html.document_fromstring(r.text)
        document.make_links_absolute(base_url)
        objects = document.body.cssselect('.obj')
        for obj in objects:
            data.append(obj.cssselect('.img')[0].get('href'))
    return data


def parse_lot(page):
    r = requests.get(page, headers=headers)
    r.encoding = "UTF-8"
    doc = lxml.html.document_fromstring(r.text)
    doc.make_links_absolute(base_url)
    lot = Lot()

    obj = doc.body.cssselect("#objInfo")[0]
    lot.id = int(page.split('/')[-1])
    lot.link = unicode(page)
    lot.type = unicode(obj.cssselect("#objInfo>h1")[0].text.split(u'Продается ')[1].strip())
    address = Address()
    address_string = obj.cssselect("#objInfo>h1>span")[0].text_content().strip().replace("  ", " ").replace("\n", " ")
    if u',' in address_string:
        address.region = address_string.split(',')[2].strip()
        address.city = address_string.split(',')[0].strip()
    else:
        address.region = " ".join(address_string.split(' ')[-2:]).strip()
        address.city = " ".join(address_string.split(' ')[:-2]).strip()
    if len(address_string.split(',')) == 3:
        address.street = address_string.split(',')[1].strip()
    lot.address = address
    main_features = obj.cssselect(".objFeatures>table")
    trs = dict()
    for table in main_features:
        for tr in table.cssselect("tr"):
            children = tr.getchildren()
            trs[children[0].text] = children[1].text
    if u'Комнат' in trs:
        lot.rooms = int(trs[u'Комнат'])
    if u'Этаж' in trs:
        lot.level = unicode(trs[u'Этаж'])
    if u'Год постройки' in trs:
        lot.build_year = unicode(trs[u'Год постройки'])
    squares = Square()
    if u'Общая площадь' in trs:
        squares.common = float(trs[u'Общая площадь'].split()[0].split(' ')[0])
    if u'Жилая площадь' in trs:
        squares.living = float(trs[u'Жилая площадь'].split(' ')[0])
    if u'Площадь кухни' in trs:
        squares.kitchen = float(trs[u'Площадь кухни'].split(' ')[0])
    if u'Площадь с/у' in trs:
        if u'/' in trs[u'Площадь с/у'].split(' ')[0]:
            squares.bathroom = float(trs[u'Площадь с/у'].split(' ')[0].split('/')[0])
            squares.toilet = float(trs[u'Площадь с/у'].split(' ')[0].split('/')[1])
        else:
            squares.wc = float(trs[u'Площадь с/у'].split(' ')[0])
    if u'Площадь земли' in trs:
        squares.territory = float(trs[u'Площадь земли'].split(' ')[0])
    if squares:
        lot.square = squares
    communications = Communication()
    if u'Водоснабжение' in trs:
        communications.water = unicode(trs[u'Водоснабжение'])
    if u'Отопление' in trs:
        communications.heat = unicode(trs[u'Отопление'])
    if u'Коммуникации' in trs:
        communications.other = unicode(trs[u'Коммуникации'])
    if communications:
        lot.communications = communications
    photos = []
    for element, attribute, link, pos in obj.cssselect('.jCarouselLite>ul')[0].iterlinks():
        if "carousel" in link:
            photos.append(unicode(link))
    if photos:
        lot.photo = photos
    lot.price = int(obj.cssselect('.objBuy>strong')[0].text.strip().replace(u"\xa0", u""))
    price2 = obj.cssselect('.objBuy>span')
    if price2 and u"В кредит" in price2[0].text_content():
        lot.price_credit = int(price2[0].text_content().strip().replace(u"\xa0", u"").split(":")[1].split(" ")[0])
    price3 = obj.cssselect(".rent")
    if price3:
        lot.price_rent = int(price3[0].text_content().replace(u"\xa0", u"").split(":")[1].split(" ")[0])
    description = obj.cssselect('.objFeatures>h2')
    if description and len(description) > 1 and description[1].text_content() == u'Описание объекта':
        lot.description = unicode(obj.cssselect('.objFeatures')[0].xpath('./text()')[-1].strip())
    lot.date = datetime.utcnow()
    lot.source = SOURCE
    return lot


def update_data():
    lot_links = get_lots_links()
    # lot_links = ['http://planetestate.com.ua/estate/8505']
    for lot in lot_links:
        lot_id = int(lot.split('/')[-1])
        curr_date = datetime.utcnow()
        lot_db = Lot.query.filter(Lot.id == lot_id).first()
        lot_parsed = parse_lot(lot)
        if lot_db == lot_parsed:
            print "ok"
            lot_db.date = curr_date
            lot_db.save()
        else:
            print "differ"
            print lot_parsed.id
            lot_parsed.date = curr_date
            lot_parsed.save()


# lot = parse_lot('http://planetestate.com.ua/estate/8505')
# lot.save()
#update_data()
# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

import requests
import lxml.html
from app.db_lib import *


base_url = "http://planetestate.com.ua/estate/sell"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
}
SOURCE = u'www.planetestate.com.ua'
BANK = u'ПриватБанк'


def get_bank():
    bank_obj = Bank()
    bank_obj.name = u'ПриватБанк'
    bank_obj.website = u'http://privatbank.ua'
    bank_obj.logo = u'https://privatbank.ua/img/logo.png'
    bank_obj = get_or_create_bank(bank_obj)
    return bank_obj


def get_lots_links():
    page_url_template = "http://planetestate.com.ua/?perpage=24&category=sell&page=%d"
    page_index = 1
    data = list()

    while True:
        try:
            r = requests.get((page_url_template % page_index), headers=headers)
            r.encoding = "UTF-8"
            document = lxml.html.document_fromstring(r.text)
            document.make_links_absolute(base_url)
            objects = document.body.cssselect('.obj')
            for obj in objects:
                data.append((obj.cssselect('.img')[0].get('href'), None, None, BANK))
            page_index += 1
        except requests.ConnectionError:
            print "Can't connect to " + str(page_url_template % page_index)
            page_index += 1
            continue
        if not document.body.cssselect('.paging>a')[-1].text == u"→":
            break
    return data


def parse_lot(page):
    try:
        r = requests.get(page, headers=headers)
        r.encoding = "UTF-8"
        if r.status_code != 200:
            print "Error parsing %s" % page
            return None
        doc = lxml.html.document_fromstring(r.text)
        doc.make_links_absolute(base_url)
        lot = {}

        obj = doc.body.cssselect("#objInfo")[0]
        lot['source_id'] = int(page.split('/')[-1])
        lot['link'] = unicode(page)
        address_string = obj.cssselect("#objInfo>h1>span")[0].text_content().strip().replace("  ", " ").replace("\n", " ")
        lot['country'] = u'Украина'
        if u',' in address_string:
            lot['region'] = address_string.split(',')[2].strip()
            lot['city'] = address_string.split(',')[0].strip()
        else:
            lot['region'] = unicode(" ".join(address_string.split(' ')[-2:]).strip())
            lot['city'] = unicode(" ".join(address_string.split(' ')[:-2]).strip())
        lot['street'] = ''
        if len(address_string.split(',')) == 3:
            lot['street'] = unicode(address_string.split(',')[1].strip())
        if obj.cssselect("#objInfo>h1")[0].text.split(u'Продается ')[1].strip() == u'':
            if u'кв.' in address_string:
                lot['type'] = u'Квартира'
            else:
                lot['type'] = u'Жилой дом'
        else:
            lot['type'] = unicode(obj.cssselect("#objInfo>h1")[0].text.split(u'Продается ')[1].strip())
        main_features = obj.cssselect(".objFeatures>table")
        trs = dict()
        for table in main_features:
            for tr in table.cssselect("tr"):
                children = tr.getchildren()
                trs[children[0].text] = children[1].text
        if u'Комнат' in trs:
            lot['rooms'] = int(trs[u'Комнат'])
        if u'Этаж' in trs:
            lot['level'] = unicode(trs[u'Этаж'])
        if u'Год постройки' in trs:
            lot['build_year'] = unicode(trs[u'Год постройки'])
        squares = dict()
        if u'Общая площадь' in trs:
            squares['common'] = float(trs[u'Общая площадь'].split()[0].split(' ')[0])
        if u'Жилая площадь' in trs:
            squares['living'] = float(trs[u'Жилая площадь'].split(' ')[0])
        if u'Площадь кухни' in trs:
            squares['kitchen'] = float(trs[u'Площадь кухни'].split(' ')[0])
        if u'Площадь с/у' in trs:
            if u'/' in trs[u'Площадь с/у'].split(' ')[0]:
                squares['bathroom'] = float(trs[u'Площадь с/у'].split(' ')[0].split('/')[0])
                squares['toilet'] = float(trs[u'Площадь с/у'].split(' ')[0].split('/')[1])
            else:
                squares['wc'] = float(trs[u'Площадь с/у'].split(' ')[0])
        if u'Площадь земли' in trs:
            squares['territory'] = float(trs[u'Площадь земли'].split(' ')[0])
        if squares:
            lot['square'] = squares
        communications = dict()
        if u'Водоснабжение' in trs:
            communications[u'water'] = unicode(trs[u'Водоснабжение'])
        if u'Отопление' in trs:
            communications[u'heat'] = unicode(trs[u'Отопление'])
        if u'Коммуникации' in trs:
            communications[u'other'] = unicode(trs[u'Коммуникации'])
        if communications:
            lot['communications'] = communications
        photos = []
        for element, attribute, link, pos in obj.cssselect('.jCarouselLite>ul')[0].iterlinks():
            if "carousel" in link:
                photos.append(unicode(link))
        if photos:
            lot['photo'] = photos
        lot['price'] = int(obj.cssselect('.objBuy>strong')[0].text.strip().replace(u"\xa0", u""))
        price2 = obj.cssselect('.objBuy>span')
        if price2 and u"В кредит" in price2[0].text_content():
            lot['price_credit'] = int(price2[0].text_content().strip().replace(u"\xa0", u"").split(":")[1].split(" ")[0])
        price3 = obj.cssselect(".rent")
        if price3:
            lot['price_rent'] = int(price3[0].text_content().replace(u"\xa0", u"").split(":")[1].split(" ")[0])
        description = obj.cssselect('.objFeatures>h2')
        if description and len(description) > 1 and description[1].text_content() == u'Описание объекта':
            lot['description'] = unicode(obj.cssselect('.objFeatures')[0].xpath('./text()')[-1].strip())
        lot['source'] = SOURCE
        return lot
    except requests.ConnectionError, e:
        print "Error parsing %s" % page
        print e
        return None

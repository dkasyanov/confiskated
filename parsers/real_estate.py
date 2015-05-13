# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

import requests
import lxml.html
from app.db_lib import *


base_url = "http://pumb.ua/ru/collateral/real_estate/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
}
SOURCE = u'www.pumb.ua/ru/collateral/real_estate/'
BANK = u'ПУМБ'
street_prefixes = [u'ул.', u'пр.', u'проезд', u'переулок', u'пер.',
                   u'улица', u'ж/м', u'бульвар', u'п-т', u'ул ', u'пл', u'пос.']


def get_bank():
    bank = Bank()
    bank.name = u'ПУМБ'
    bank.website = u'http://pumb.ua/'
    bank.logo = u'https://online.pumb.ua/Pages/Login/img/logo/ib_logo.gif'
    bank = get_or_create_bank(bank)
    return bank


def get_lots_links():
    page_url_templates = ["http://pumb.ua/ru/collateral/real_estate/?PAGEN_1=%d", "http://pumb.ua/ru/collateral/commercial_estate/?PAGEN_1=%d"]

    data = list()
    for page in page_url_templates:
        page_index = 1
        while True:
            try:
                r = requests.get((page % page_index), headers=headers)
                r.encoding = "UTF-8"
                document = lxml.html.document_fromstring(r.text)
                document.make_links_absolute(base_url)
                objects = document.body.cssselect('.text')
                for obj in objects:
                    if len(obj.cssselect('b>a')):
                        link = obj.cssselect('b>a')[0].get('href')
                        region = obj.cssselect('.adr')[0].text.split(',')[0].strip()
                        city = obj.cssselect('.adr')[0].text.split(',')[1].strip()
                        if u'Крым' in region:
                            region = u'Крым'
                        else:
                            region += u' область'
                        data.append((link, region, city, BANK))
                page_index += 1
            except requests.ConnectionError:
                print "Can't connect to " + str(page % page_index)
                page_index += 1
                continue
            if len(document.body.cssselect('.next-month.disabled')) == 1:
                break
    return data


def parse_lot(page, region, city):
    try:
        r = requests.get(page, headers=headers)
        r.encoding = "UTF-8"
        if r.status_code != 200:
            print "Error parsing %s" % page
            return None
        doc = lxml.html.document_fromstring(r.text)
        doc.make_links_absolute(base_url)
        lot = {}

        obj = doc.body.cssselect(".mortgaged-property-inside")[0]
        lot['source_id'] = int(page.split('/')[-2].replace('_', '').replace('-', ''))
        lot['link'] = unicode(page)
        if unicode(u'Коммерческая недвижимость') in doc.body.cssselect("#page-title")[0].text:
            lot['type'] = u'Коммерческая недвижимость'
        else:
            type_parsed = unicode(obj.cssselect("#fototitle")[0].text.strip())
            if type_parsed == u'Дом':
                type_parsed = u'Жилой дом'
            lot['type'] = type_parsed
        country = u'Украина'
        region = region
        city = city
        address_string = obj.cssselect(".mp-info>ul>li")[0].text_content()
        street = None
        if u'Адрес:' in address_string:
            address_string = address_string.split(u'Адрес:')[1].strip()
            for delimiter in street_prefixes:
                if delimiter in address_string:
                    street = unicode(address_string[address_string.index(delimiter):].strip())
                    break
            if not street:
                print "Error: Can't find street: " + address_string
                street = u''
        else:
            print "Error: Can't find street: " + address_string
            street = u''
        lot['street'] = street
        main_features = obj.cssselect(".mp-properties>table")
        trs = dict()
        for table in main_features:
            for tr in table.cssselect("tr"):
                children = tr.getchildren()
                trs[children[0].text] = children[1].text
        if u'Кол-во комнат' in trs:
            lot['rooms'] = int(trs[u'Кол-во комнат'])
        if u'Этаж' in trs:
            if u'Всего этажей' in trs:
                lot['level'] = unicode(trs[u'Этаж'] + '/' + trs[u'Всего этажей'])
            else:
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
        if len(obj.cssselect('.mp-gallery')) > 0:
            for element, attribute, link, pos in obj.cssselect('.mp-gallery')[0].iterlinks():
                if "jpg" in link and "resize" not in link:
                    photos.append(unicode(link))
        if photos:
            lot['photo'] = photos
        lot['price'] = int(obj.cssselect('.txt>b')[0].text.split(u' грн')[0].strip().replace(u"\xa0", u"").split(u'.')[0].replace(' ', ''))
        lot['description'] = unicode(obj.cssselect('.mp-info>ul>li')[1].xpath('./text()')[-1].strip())
        lot['source'] = SOURCE
        return lot
    except requests.ConnectionError, e:
        print "Error parsing %s" % page
        print e
        return None

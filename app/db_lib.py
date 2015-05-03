# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

from app.models import Lot, Address, Country, Region, City, Type, Square, Bank
from app import db


def get_type(data):
    t = Type.query.filter_by(name=data).first()
    if not t:
        new_type = Type(name=data)
        db.session.add(new_type)
        db.session.commit()
        return new_type
    return t


def get_country(country_name):
    country = Country.query.filter_by(name=country_name).first()
    if not country:
        new_country = Country(name=country_name)
        db.session.add(new_country)
        db.session.commit()
        return new_country
    return country


def get_region(region_name, country):
    region = Region.query.filter_by(name=region_name, country_id=country.id).first()
    if not region:
        new_region = Region(name=region_name, country_id=country.id)
        db.session.add(new_region)
        db.session.commit()
        return new_region
    return region


def get_city(city_name, region):
    city = City.query.filter_by(name=city_name, region_id=region.id).first()
    if not city:
        new_city = City(name=city_name, region_id=region.id)
        db.session.add(new_city)
        db.session.commit()
        return new_city
    return city


def get_address(country, region, city, street='', other=''):
    address = Address.query.filter_by(country_id=country.id, region_id=region.id, city_id=city.id, street=street, other=other).first()
    if not address:
        new_address = Address(country=country, country_id=country.id,
                              region=region, region_id=region.id,
                              city=city, city_id=city.id,
                              street=street, other=other)
        db.session.add(new_address)
        db.session.commit()
        return new_address
    return address


def get_square(square):
    sq = Square.query.filter_by(common=square.common, living=square.living,
                                kitchen=square.kitchen, bathroom=square.bathroom,
                                toilet=square.toilet, wc=square.wc, territory=square.territory).first()
    if not sq:
        db.session.add(square)
        db.session.commit()
        return square
    return sq


def get_or_create_bank(bank):
    _bank = Bank.query.filter_by(name=bank.name, website=bank.website).first()
    if not _bank:
        db.session.add(bank)
        db.session.commit()
        return bank
    return _bank
# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'

from app.models import Address, Country, Region, City, Type, Square, Bank
from app import db_session


def get_or_create_type(data):
    session = db_session()
    t = session.query(Type).filter_by(name=data).first()
    if not t:
        new_type = Type(name=data)
        session.add(new_type)
        session.commit()
        session.expunge_all()
        session.close()
        return new_type
    session.expunge_all()
    session.close()
    return t


def get_or_create_country(country_name):
    session = db_session()
    country = session.query(Country).filter_by(name=country_name).first()
    if not country:
        new_country = Country(name=country_name)
        session.add(new_country)
        session.commit()
        session.expunge_all()
        session.close()
        return new_country
    session.expunge_all()
    session.close()
    return country


def get_or_create_region(region_name, country):
    session = db_session()
    session.add(country)
    region = session.query(Region).filter_by(name=region_name, country_id=country.id).first()
    if not region:
        new_region = Region(name=region_name, country_id=country.id)
        session.add(new_region)
        session.commit()
        session.expunge_all()
        session.close()
        return new_region
    session.expunge_all()
    session.close()
    return region


def get_or_create_city(city_name, region):
    session = db_session()
    city = session.query(City).filter_by(name=city_name, region_id=region.id).first()
    if not city:
        new_city = City(name=city_name, region_id=region.id)
        session.add(new_city)
        session.commit()
        session.expunge_all()
        session.close()
        return new_city
    session.expunge_all()
    session.close()
    return city


def get_or_create_address(country, region, city, street='', other=''):
    session = db_session()
    session.add(country)
    session.add(region)
    session.add(city)
    address = session.query(Address).filter_by(country_id=country.id, region_id=region.id, city_id=city.id, street=street, other=other).first()
    if not address:
        new_address = Address(country=country, country_id=country.id,
                              region=region, region_id=region.id,
                              city=city, city_id=city.id,
                              street=street, other=other)
        session.add(new_address)
        session.commit()
        session.expunge_all()
        session.close()
        return new_address
    session.expunge_all()
    session.close()
    return address


def get_or_create_square(square):
    session = db_session()
    sq = session.query(Square).filter_by(common=square.common, living=square.living,
                                         kitchen=square.kitchen, bathroom=square.bathroom,
                                         toilet=square.toilet, wc=square.wc,
                                         territory=square.territory).first()
    if not sq:
        session.add(square)
        session.commit()
        session.expunge_all()
        session.close()
        return square
    session.expunge_all()
    session.close()
    return sq


def get_or_create_bank(bank):
    session = db_session()
    _bank = session.query(Bank).filter_by(name=bank.name, website=bank.website).first()
    if not _bank:
        session.add(bank)
        session.commit()
        session.close()
        session.expunge_all()
        return bank
    session.expunge_all()
    session.close()
    return _bank
# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import db


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    country = db.relationship('Country')
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    region = db.relationship('Region')
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')
    street = db.Column(db.String(128), default='')
    other = db.Column(db.String(128), default='')


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    regions = db.relationship('Region', backref='country', lazy='dynamic')


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    cities = db.relationship('City', backref='region', lazy='dynamic')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))


class Square(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common = db.Column(db.Float)
    living = db.Column(db.Float)
    kitchen = db.Column(db.Float)
    bathroom = db.Column(db.Float)
    toilet = db.Column(db.Float)
    wc = db.Column(db.Float)
    territory = db.Column(db.Float)


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)


class Photo(db.Model):
    photo_id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(256), unique=True)


class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    website = db.Column(db.String(120))
    logo = db.Column(db.String(256))


class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer)
    link = db.Column(db.String(128))
    type = db.relationship('Type')
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    address = db.relationship('Address')
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    square = db.relationship('Square')
    square_id = db.Column(db.Integer, db.ForeignKey('square.id'))
    communications = db.Column(db.PickleType)
    rooms = db.Column(db.Integer, default=-1)
    level = db.Column(db.String(8))
    build_year = db.Column(db.String(4))
    description = db.Column(db.String(512))
    photo = db.Column(db.PickleType)
    price = db.Column(db.Integer)
    price_credit = db.Column(db.Integer)
    price_rent = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    source = db.Column(db.String(128))
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    bank = db.relationship('Bank')

    def get_attributes(self):
        return [k for k in self.__dict__.keys()
                if not k.startswith('_')
                and not k.endswith('_')]

    def compare(self, other):
        if not self or not other:
            return False
        for attr in self.get_attributes():
            if attr == 'date' or attr == 'id':
                continue
            if self.__getattribute__(attr) != other.__getattribute__(attr):
                return False
        return True
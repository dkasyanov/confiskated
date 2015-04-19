# -*- coding: utf-8 -*-
__author__ = 'dkasyanov'
from app import db
from mongoalchemy.fields import IntField, StringField, DocumentField, DictField, FloatField, ListField, DateTimeField
import datetime


class Address(db.Document):
    country = StringField(default=u'Украина')
    region = StringField(default='')
    city = StringField(default='')
    street = StringField(default='')
    other = StringField(default='')


class Square(db.Document):
    common = FloatField(default=-1)
    living = FloatField(default=-1)
    kitchen = FloatField(default=-1)
    bathroom = FloatField(default=-1)
    toilet = FloatField(default=-1)
    wc = FloatField(default=-1)
    territory = FloatField(default=-1)


class Communication(db.Document):
    water = StringField(default='')
    heat = StringField(default='')
    other = StringField(default='')


class Lot(db.Document):
    id = IntField()
    link = StringField()
    type = StringField()
    address = DocumentField(Address)
    square = DocumentField(Square, default=None)
    communications = DocumentField(Communication, default=None)
    rooms = IntField(default=-1)
    level = StringField(default='')
    build_year = StringField(default='')
    description = StringField(default='')
    photo = ListField(StringField(), default=[])
    price = IntField()
    price_credit = IntField(default=-1)
    price_rent = IntField(default=-1)
    date = DateTimeField()
    source = StringField(default='')

    def get_attributes(self):
        return [k for k in self.__dict__.keys()
                if not k.startswith('_')
                and not k.endswith('_')]

    def __eq__(self, other):
        if not self or not other:
            return False
        for attr in self.get_attributes():
            if attr == 'date':
                continue
            if self.__getattribute__(attr) != other.__getattribute__(attr):
                return False
        return True
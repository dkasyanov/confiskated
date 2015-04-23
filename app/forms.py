__author__ = 'dkasyanov'
from flask.ext.wtf import Form
from wtforms import SelectField, StringField, BooleanField, FloatField, IntegerField


class FiltersForm(Form):
    regionSelector = SelectField(u"regions", coerce=int)
    citySelector = SelectField(u"cities", coerce=int)
    typeSelector = SelectField(u"Type", coerce=int)
    room1 = BooleanField(u'room1', default=False)
    room2 = BooleanField(u'room2', default=False)
    room3 = BooleanField(u'room3', default=False)
    room4 = BooleanField(u'room4', default=False)
    price_from = IntegerField(u'Price from')
    price_to = IntegerField(u'Price to')
    square_from = FloatField(u'Square from')
    square_to = FloatField(u'Square to')
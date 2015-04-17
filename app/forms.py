__author__ = 'dkasyanov'
from flask.ext.wtf import Form
from wtforms import SelectField, StringField, BooleanField


class FiltersForm(Form):
    regions = [('1', '2'), ('3', '4'), ('5', '6')]
    cities = []
    regionSelector = SelectField(u"regions", choices=regions)
    citySelector = SelectField(u"cities", choices=cities)
    typeSelector = SelectField(u"Type", choices=[])
    room1 = BooleanField(u'room1', default=False)
    room2 = BooleanField(u'room2', default=False)
    room3 = BooleanField(u'room3', default=False)
    room4 = BooleanField(u'room4', default=False)
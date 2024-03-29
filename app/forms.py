__author__ = 'dkasyanov'
from flask.ext.wtf import Form
from wtforms import SelectField, BooleanField, FloatField, IntegerField, StringField
from wtforms.widgets import TextArea



class FiltersForm(Form):
    regionSelector = SelectField(u"regions", coerce=int)
    citySelector = SelectField(u"cities", coerce=int)
    typeSelector = SelectField(u"Type", coerce=int)
    bankSelector = SelectField(u'Bank', coerce=int)
    room1 = BooleanField(u'room1', default=False)
    room2 = BooleanField(u'room2', default=False)
    room3 = BooleanField(u'room3', default=False)
    room4 = BooleanField(u'room4', default=False)
    price_from = IntegerField(u'Price from')
    price_to = IntegerField(u'Price to')
    square_from = FloatField(u'Square from')
    square_to = FloatField(u'Square to')


class FeedbackForm(Form):
    user_name = StringField(u'username')
    user_email = StringField(u'email')
    text_comment = StringField(u'textarea', widget=TextArea())
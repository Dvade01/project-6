from mongoengine import *


class Control_Point(EmbeddedDocument):
    miles = FloatField(required=True)
    km = FloatField(required=True)
    location = StringField()
    open = StringField(required=True)
    close = StringField(required=True)

class Brevet(Document):
    brevet = FloatField(required=True)
    start = StringField(required=True)
    control_pts = EmbeddedDocumentListField(Control_Point, required=True)
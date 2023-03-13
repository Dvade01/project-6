from mongoengine import *


class Checkpoint(EmbeddedDocument):
    """
    Class that defines a control point for a brevet.

    Attributes:
        miles (float): the distance of the control point in miles (optional)
        km (float): the distance of the control point in kilometers (required)
        open (str): the opening time of the control point in HH:MM format (required)
        close (str): the closing time of the control point in HH:MM format (required)
        location (str): the name or description of the location of the control point (optional)
    """
    miles = FloatField(required=False)
    km = FloatField(required=True)
    open = StringField(required=True)
    close = StringField(required=True)
    location = StringField(required=False)


class Brevet(Document):
    """
    Class that defines a brevet table.

    Attributes:
        brev_km_dist (float): the distance of the brevet in kilometers (required)
        brev_start_date (str): the starting date of the brevet in YYYY-MM-DD format (required)
        control_pts (list): a list of Control objects representing the control points of the brevet (required)
    """
    brev_km_dist = FloatField(required=True)
    brev_start_date = StringField(required=True)
    control_pts = EmbeddedDocumentListField(Checkpoint, required=True)

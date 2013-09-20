from mongoengine import connect, Document
from mongoengine.fields import DecimalField, StringField, PointField

# TODO: Don't hardcode the database name
connect('hoops')

class Court(Document):
    name = StringField(required=True)
    point = PointField()

    meta = {'allow_inheritance': True}

    def to_geojson(self):
        json = {
            'type': 'Feature',
            'geometry': self.point,
            'properties': {
                 'name': self.name,
             },
        }
        return json

class ParkDistrictCourt(Court):
    official_name = StringField(required=True)
    park_num = DecimalField(required=True)
    facility_type = StringField()

import json

from mongoengine import connect, Document, QuerySet
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

class ParkDistrictCourtQuerySet(QuerySet):
    def cluster(self, radius):
        # http://docs.mongoengine.org/en/latest/guide/querying.html
        seen = set()
        clusters = []
        for hoop in self.all():
            if hoop.id not in seen:
                cluster = {
                    'name': hoop.name,
                    'hoops': [],
                    'centroid': None
                }
                sum_x = 0
                sum_y = 0
                x = hoop.point['coordinates'][0]
                y = hoop.point['coordinates'][1]
                nearby_hoops = self.filter(
                    point__geo_within_center=[(x, y), radius])
                       
                for nearby in nearby_hoops:
                    sum_x += x
                    sum_y += y
                    cluster['hoops'].append(nearby)
                    seen.add(nearby.id)

                num_hoops = len(cluster['hoops'])
                cluster['centroid'] = [sum_x / num_hoops, sum_y / num_hoops]
                clusters.append(cluster)

        return clusters

    def to_geojson(self, cluster_radius):
        clusters = self.cluster(cluster_radius)
        simplified = []
        for cluster in clusters:
            simplified.append({
                'type': 'Feature',
                'geometry': {
                  'type': 'Point',
                  'coordinates': [cluster['centroid'][0], cluster['centroid'][1]],
                },
                'properties': {
                    'name': cluster['name'],
                    'count': len(cluster['hoops']),
                },
            })
        return json.dumps({
            'type': 'FeatureCollection',
            'features': [cluster for cluster in simplified],
        })

class ParkDistrictCourt(Court):
    official_name = StringField(required=True)
    park_num = DecimalField(required=True)
    facility_type = StringField()
    facility_name = StringField()

    meta = {'queryset_class': ParkDistrictCourtQuerySet}

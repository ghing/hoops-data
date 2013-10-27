from decimal import Decimal
import json

from csvkit import CSVKitReader
from csvkit.grep import FilteringCSVReader

from models import ParkDistrictCourt

def split_location(val):
    # Remove whitespace, parenthesis from location column
    location = val.strip().lstrip('(').rstrip(')')
    parts = location.split(',')
    return float(Decimal(parts[0])), float(Decimal(parts[1]))

def load_park_district_courts(csv_file):
    rows = CSVKitReader(csv_file)
    patterns = {
        'FACILITY NAME': 'BASKETBALL',
    }
    # HACK: More human-readable indexes into fields in the rows of
    # the CSV file.  Maybe there's a DictReader subclass that let's one
    # index by column name, or a method of ``CSVKitReader`` that
    # resolves column indexes from their names
    name_index = 0
    number_index = 1 
    type_index = 3
    location_index = 6

    filter_reader = FilteringCSVReader(rows, patterns=patterns, header=True)
    filter_reader.next() # Skip header

    for row in filter_reader:
        lat, lng = split_location(row[location_index])
        court = ParkDistrictCourt(
            name=row[name_index],
            point=[lng, lat],
            official_name=row[name_index],
            park_num=row[number_index],
            facility_type=row[type_index],
        )
        court.save()

def dump_park_district_courts():
    # HACK: Personally, I think this makes more sense to have this be with
    # the model
    return json.dumps({
        'type': 'FeatureCollection',
        'features': [c.to_geojson() for c in ParkDistrictCourt.objects()],
    })

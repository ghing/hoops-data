from decimal import Decimal

from csvkit import CSVKitReader
from csvkit.grep import FilteringCSVReader

from models.official import ParkDistrictCourt
from models.census import TigerTract

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
    facility_name_index = 2
    facility_type_index = 3
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
            facility_name=row[facility_name_index],
            facility_type=row[facility_type_index],
        )
        court.save()

def dump_park_district_courts():
    return ParkDistrictCourt.objects(facility_name__contains="BACKBOARD").as_geojson(.001)

def clear_park_district_courts():
    ParkDistrictCourt.objects.delete()

def dump_tracts():
    return TigerTract.query.as_geojson()

def _tract_stats_row(tract):
    return {
        "geoid": tract.geoid,
        "total": tract.p12_data.total,
        "kids": tract.p12_data.all_kids,
        "younger_kids": tract.p12_data.younger_kids,
        "older_kids": tract.p12_data.older_kids,
        "pct_older_kids": tract.p12_data.pct_older_kids,
    }

def dump_tract_stats_as_csv():
    tracts = TigerTract.query.all()
    rows = map(_tract_stats_row, tracts)
    return rows

def _aggregate_tract_stats(accumulated, current):
    accumulated['younger_kids'] += current.p12_data.younger_kids
    accumulated['older_kids'] += current.p12_data.older_kids
    return accumulated

def chicago_summary():
    summary = {
        'younger_kids': 0,
        'older_kids': 0,
    }
    tracts = TigerTract.query.all()
    return reduce(_aggregate_tract_stats, tracts, summary)

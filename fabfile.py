import sys

from fabric.api import local, task
from fabric.contrib.console import confirm
import requests

from hoops_data import data

@task
def load_park_district_courts(filename):
    with open(filename, 'r') as csv_file:
        data.load_park_district_courts(csv_file)

@task
def dump_park_district_courts(filename=None):
    if filename is None:
        f = sys.stdout
        f.write(data.dump_park_district_courts())
    else:
        with open(filename, 'w') as f:
            f.write(data.dump_park_district_courts())

@task
def clear_park_district_courts():
    response = confirm("Are you sure you want to clear ALL park district courts?")
    data.clear_park_district_courts()


@task
def validate_geojson(filename):
    validate_endpoint = 'http://geojsonlint.com/validate'

    with open(filename, 'r') as f:
        data = f.read()
        r = requests.post(validate_endpoint, data=data)
        r_json = r.json()
        if r_json['status'] == 'ok':
            sys.stdout.write("Valid GeoJSON")
        else:
            sys.stdout.write("Invalid GeoJSON")

@task
def load_census_data():
    local("./bin/load_sqlite.sh P12 17 140 hoops.db")

@task
def load_chicago_tract_shapes():
    local("ogr2ogr -update -f SQLite "
          "hoops.dbdata/CensusTracts2010/CensusTractsTIGER2010.shp")


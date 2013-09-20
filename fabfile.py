import sys

from fabric.api import local, task
import requests

import data

@task
def load_data(filename):
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

from __future__ import division

import json

from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import Query, relationship, foreign
from geoalchemy import GeometryColumn, Geometry 
import shapely.wkt
from shapely.geometry import mapping

from hoops_data.database import db_session 


class CensusTableMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        table = 'p012'
        for i in range(1, 49):
            fname = "%s%03d" % (table, i)
            dict_[fname] = Column(Integer)
            setattr(cls, fname, dict_[fname])
        super(CensusTableMeta, cls).__init__(classname, bases, dict_)


class TractQuery(Query):
    def as_geojson_dict(self):
        return {
            "type": "FeatureCollection",
            "features": [feature.as_geojson_dict() for feature in self],
        }

    def as_geojson(self):
        return json.dumps(self.as_geojson_dict())


metadata = MetaData(db_session.get_bind())

CensusTableBase = declarative_base(metaclass=CensusTableMeta, metadata=metadata)
CensusTableBase.query = db_session.query_property()

Base = declarative_base(metadata=metadata)
Base.query = db_session.query_property(query_cls=TractQuery)

class P12Data(CensusTableBase):
    __tablename__ = 'ire_p12'

    geoid = Column(String(12), primary_key=True)

    @property
    def total(self):
        return self.p012001

    @property
    def male_under_5(self):
        return self.p012003

    @property
    def male_5_to_9(self):
        return self.p012004

    @property
    def male_10_to_14(self):
        return self.p012005

    @property
    def male_15_to_17(self):
        return self.p012006

    @property
    def male_18_to_19(self):
        return self.p012007

    @property
    def fem_under_5(self):
        return self.p012027

    @property
    def fem_5_to_9(self):
        return self.p012028

    @property
    def fem_10_to_14(self):
        return self.p012029

    @property
    def fem_15_to_17(self):
        return self.p012030

    @property
    def fem_18_to_19(self):
        return self.p012031

    @property
    def all_under_5(self):
        return self.male_under_5 + self.fem_under_5

    @property
    def all_5_to_9(self):
        return self.male_5_to_9 + self.fem_5_to_9

    @property
    def all_10_to_14(self):
        return self.male_10_to_14 + self.fem_10_to_14 

    @property
    def all_15_to_17(self):
        return self.male_15_to_17 + self.fem_15_to_17

    @property
    def all_18_to_19(self):
        return self.male_18_to_19 + self.fem_18_to_19

    @property
    def all_kids(self):
        return (self.all_under_5 + self.all_5_to_9 + self.all_10_to_14 +
               self.all_15_to_17 + self.all_18_to_19)

    @property
    def younger_kids(self):
        return self.all_under_5 + self.all_5_to_9

    @property
    def older_kids(self):
        return self.all_10_to_14 + self.all_15_to_17

    @property
    def pct_older_kids(self):
        if self.total > 0:
            return self.older_kids / self.total

        return 0


class TigerTract(Base):
    __tablename__ = 'censustractstiger2010'

    ogc_fid = Column(Integer, primary_key=True)
    geoid = Column('geoid10', String)
    geom = GeometryColumn('GEOMETRY', Geometry(2))

    def as_mapping(self):
       return mapping(shapely.wkt.loads(db_session.scalar(self.geom.wkt)))

    def as_geojson_dict(self):
        return {
            "type": "Feature",
            "geometry": self.as_mapping(),
            "properties": {
                "geoid": self.geoid,
                "total": self.p12_data.total,
                "kids": self.p12_data.all_kids,
                "younger_kids": self.p12_data.younger_kids,
                "older_kids": self.p12_data.older_kids,
                "pct_older_kids": self.p12_data.pct_older_kids,
            }
        }

    def as_geojson(self):
        return json.dumps(self.as_geojson_dict())

TigerTract.p12_data = relationship(P12Data,
            uselist=False,
            primaryjoin=P12Data.geoid==foreign(TigerTract.geoid))

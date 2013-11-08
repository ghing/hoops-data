from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm import Query
from sqlalchemy.sql import exists

from hoops_data.database import db_session 

class CensusTableMeta(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        table = 'p012'
        for i in range(1, 49):
            fname = "%s%03d" % (table, i)
            dict_[fname] = Column(Integer)
            setattr(cls, fname, dict_[fname])
        super(CensusTableMeta, cls).__init__(classname, bases, dict_)


class P12TractQuery(Query):
    def has_shape(self):
        stmt = exists().where(TigerTract.geoid==P12Tract.geoid)
        return self.filter(stmt)


CensusTableBase = declarative_base(metaclass=CensusTableMeta) 
CensusTableBase.query = db_session.query_property(query_cls=P12TractQuery)

Base = declarative_base()
Base.query = db_session.query_property()

class P12Tract(CensusTableBase):
    __tablename__ = 'ire_p12'

    geoid = Column(String(12), primary_key=True)

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



class TigerTract(Base):
    __tablename__ = 'censustractstiger2010'

    ogc_fid = Column(Integer, primary_key=True)
    geoid = Column('geoid10', String)

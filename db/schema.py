from __future__ import annotations

from enum import Enum, unique
from dataclasses import (dataclass, field)
from typing import List


from sqlalchemy import (
    Column, Date, Enum as OraEnum, ForeignKey, ForeignKeyConstraint, Integer,
    MetaData, String, Table, Numeric, orm, DateTime, Identity,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, backref, registry
from sqlalchemy import create_mock_engine, create_engine


mapper_registry = registry()


# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base()

def dump(sql, *multiparams, **params):
    print(sql.compile(dialect=engine.dialect))

#engine = create_mock_engine('oracle+cx_oracle://', dump)
#engine = create_mock_engine('sqlite://', dump)
CONNECTION_STRING = 'sqlite:///db2prometheus'
#CONNECTION_STRING = 'sqlite:///:memory:'
#engine = create_engine('sqlite:///:memory:', echo=True)

class BaseMetric(Base):
#    __abstract__ = True
    metadata = metadata
    __tablename__ = 'base_metrics'
    __mapper_args__ = {
        'polymorphic_identity':'base_metric',
        'polymorphic_on':'type'
    }
    id = Column(Integer, Identity(start=3), primary_key=True)
    type = Column(String(50))
    name  = Column(String(64))
    value = Column(Numeric)
    last_update_date = Column(DateTime)
    description = Column(String(256))
    labels = orm.relationship('Label')
    def __repr__(self):
        return "Metric(metric_type:'{self.type}',\
         metric_name:'{self.name}', metric_value:'{self.value}'".format(self=self)

class Gauge(BaseMetric):
    metadata = metadata
    __tablename__ = 'gauge_metrics'
    id = Column(Integer, ForeignKey('base_metrics.id'), primary_key = True)
    __mapper_args__ = {
        'polymorphic_identity':'gauge',
    }

class Counter(BaseMetric):
    metadata = metadata
    __tablename__ = 'counter_metrics'
    id = Column(Integer, ForeignKey('base_metrics.id'), primary_key = True)
    __mapper_args__ = {
        'polymorphic_identity':'counter',
    }

class Info (BaseMetric):
    metadata = metadata
    __tablename__ = 'info_metrics'
    id = Column(Integer, ForeignKey('base_metrics.id'), primary_key = True)
    __mapper_args__ = {
        'polymorphic_identity':'info',
    }

class Summary (BaseMetric):
    metadata = metadata
    __tablename__ = 'summary_metrics'
    id = Column(Integer, ForeignKey('base_metrics.id'), primary_key = True)
    __mapper_args__ = {
        'polymorphic_identity':'summary',
    }

@mapper_registry.mapped
@dataclass
class Bucket(Base):
    metadata = metadata
    __tablename__ = 'buckets'
    __sa_dataclass_metadata_key__="sa"
    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
    value_le: float = field(init=False, metadata={"sa": Column(Numeric)})
#    histogram_id: int = field(init = False, metadata={"sa": Column(ForeignKey("histogram_metrics.id"))})
    histograms: List[Histogram] = field(default_factory=list, metadata={"sa":relationship("Histogram")})

@mapper_registry.mapped
@dataclass
class Histogram (BaseMetric):
    metadata = metadata
    __tablename__ = 'histogram_metrics'
    __sa_dataclass_metadata_key__="sa"
    id: int = field(init = False, metadata={"sa":Column(Integer, primary_key=True)})
    bucket_id: int = field(init = False, metadata={"sa": Column(ForeignKey("buckets.id"))})
    __mapper_args__ = {
         'polymorphic_identity':'histogram',
    }

class Label(Base):
    __tablename__ = 'labels'
    metadata = metadata
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('base_metrics.id'))


class DataAccessLayer:
    def __init__(self):
        self.engine = None
        self.conn_string = CONNECTION_STRING

    def connect(self):
        self.engine = create_engine(self.conn_string, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind = self.engine)
        self.Session.configure(bind = self.engine)
#        self.session = Session.configure(bind = self.engine)

    # def createSession(self):
    #     Session = sessionmaker()
    #     self.session = Session.configure(bind=self.engine)

dal = DataAccessLayer()
dal.connect()
metadata.drop_all(dal.engine, checkfirst=False)
metadata.create_all(dal.engine, checkfirst=False)

def prep_db(session):
    b1 = Bucket( value_le = 100.00)
    b2 = Bucket( value_le = 120.00)
    b3 = Bucket( value_le = 150.00)

#    h1 = Histogram( bucket = b1 )


    with session:
        session.bulk_save_objects([b1, b2, b3])
        session.add(h1)
        session.commit()

session = dal.Session()
prep_db(session)
#prep_db(Session(dal.session).bulk_save_objects(m1))
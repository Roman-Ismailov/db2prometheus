from __future__ import annotations
import abc
from datetime import  datetime
import copy
from dataclasses import dataclass
from dataclasses import field
from typing import List


from sqlalchemy.ext.declarative import declared_attr


from sqlalchemy import (
    Column, ForeignKey, Integer,
    MetaData, String, Float, Identity, DateTime, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship,  registry, declarative_mixin

from sqlalchemy import  create_engine

import apl_naming_conventions as nc


CONNECTION_STRING = 'sqlite:///db2prometheus'

mapper_registry = registry()

metadata = MetaData(naming_convention=nc.db_objects_nc)
Base = declarative_base()

@declarative_mixin
@dataclass
#todo use mixins
class TableMixin:
    """"
    A class used to mixin standard attributes to tables
    see https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    metadata=metadata
    __sa_dataclass_metadata_key__ = "sa"
    __table_args__ = {}
    __mapper_args__ = {}
    id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )


@mapper_registry.mapped
@dataclass
class BaseMetric(abc.ABC):
    """"
    A class used to represent common prometheus metric attributes
    Attributes
    ----------
    Methods
    -------
    """
    __tablename__="base_metrics"
    metadata = metadata
    __sa_dataclass_metadata_key__ = "sa"
    __mapper_args__ = {
        'polymorphic_identity':'base_metric',
        'polymorphic_on':'type'
    }
    __table_args__ = (
        UniqueConstraint('metric_name'),
    )
    id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )
    type = Column(String(50), nullable=False)
    metric_name:str = field(default=None, metadata={"sa":Column(String(64), nullable=False)})
    last_updated:datetime = field(default=None, metadata={"sa":Column(DateTime, nullable=False)})
    last_collected:datetime = field(default=None, metadata={"sa":Column(DateTime, nullable=True)})
    collect_interval_seconds:int = field(default=None, metadata={"sa":Column(Integer, nullable=False)})
    description : str = field(default=None, metadata={"sa":Column(String(256), nullable=False)})

@mapper_registry.mapped
@dataclass
class BaseLabel(abc.ABC):
    __tablename__ = 'base_labels'
    metadata = metadata
    __sa_dataclass_metadata_key__ = "sa"
    __mapper_args__ = {
        'polymorphic_identity':'base_label',
        'polymorphic_on':'type'
    }
    id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )
    metric_id = Column(Integer, ForeignKey('base_metrics.id'))
    type = Column(String(50), nullable=False)
#    metrics: List[BaseMetric] = field(default_factory=list, metadata={"sa":relationship("base_metrics.id")})
#    metric_id = Column(Integer, ForeignKey('base_metrics.id'))


@mapper_registry.mapped
@dataclass
class TextLabel(BaseLabel):
    __tablename__ = 'text_labels'
    __table_args__ = (
        UniqueConstraint('label_name', 'label_value',  name='ux_text_labels'),
    )
    metadata = metadata
    __sa_dataclass_metadata_key__ = "sa"
    id: int = field(
        init=False, metadata={"sa": Column(Integer, Identity(start=1), ForeignKey ('base_labels.id'), primary_key=True)}
    )
    label_name : str = field(default=None, metadata={"sa":Column(String(64), nullable=False)})
    label_value : str = field(default=None, metadata={"sa":Column(String(64), nullable=False)})
    __mapper_args__ = {
        'polymorphic_identity':'text_label',
    }


@mapper_registry.mapped
@dataclass
class BucketLabel(BaseLabel):
    __tablename__ = "bucket_labels"
    __sa_dataclass_metadata_key__ = "sa"
    metadata=metadata
    id: int = field(
        init=False, metadata={"sa": Column(Integer, Identity(start=1), ForeignKey ('base_labels.id'), primary_key=True)}
    )
    bucket_value: float = field(default = None, metadata={"sa":Column(Float)})
    __mapper_args__ = {
        'polymorphic_identity':'bucket_label',
    }

@mapper_registry.mapped
@dataclass
class Gauge(BaseMetric):
    __tablename__ = "gauges"
    metadata = metadata
    __sa_dataclass_metadata_key__ = "sa"
    id: int = field(
        init=False, metadata={"sa": Column(Integer, Identity(start=1), ForeignKey ('base_metrics.id'), primary_key=True)}
    )
    value: float = field (default = None, metadata={"sa":Column(Float, nullable=False)})
    labels: List[Label] = field(default_factory=list, metadata={"sa": relationship("TextLabel")})
    __mapper_args__ = {
        'polymorphic_identity':'gauge',
    }


@mapper_registry.mapped
@dataclass
class Histogram(BaseMetric):
    __tablename__="histograms"
    metadata = metadata
    __sa_dataclass_metadata_key__ = "sa"
    id: int = field(
        init=False, metadata={"sa": Column(Integer, Identity(start=1), ForeignKey ('base_metrics.id'), primary_key=True)}
    )
    #metric_name:str = field(default=None, metadata={"sa":Column(String(50), nullable=False)})
    value: float = field (default = None, metadata={"sa":Column(Float, nullable=False)})
    labels: List[TextLabel] = field(default_factory=list, metadata={"sa": relationship("TextLabel")})
    buckets: List[BucketLabel] = field(default_factory=list, metadata={"sa": relationship("BucketLabel")})
    __mapper_args__ = {
        'polymorphic_identity':'histogram',
    }



class DataAccessLayer:
    def __init__(self):
        self.engine = None
        self.conn_string = CONNECTION_STRING

    def connect(self):
        self.engine = create_engine(self.conn_string, echo=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind = self.engine)
        self.Session.configure(bind = self.engine)


dal = DataAccessLayer()
dal.connect()
metadata.drop_all(dal.engine, checkfirst=True)
metadata.create_all(dal.engine, checkfirst=False)

def prep_db(session):

    m1 = Gauge('GINI', datetime.now(), None, 15*60
               , 'GINI - вероятность того, что конкретная переменная будет неправильно классифицирована при ее случайном выборе')
    l1 = TextLabel('ml_model_name', 'deep_blue')
    l2 = TextLabel('ml_model_name', 'alpha_go')
    l3 = TextLabel('ml_model_name', 'Kasparov_pow_10')
    m1.labels = [l1, l2, l3]
    m1.value = float(1.01)

    m2 = Gauge('app_version_info', datetime.now(),None, 15*60, 'Версия приложения')
    l4 = TextLabel('team_name', 'apl_products')
    l5 = TextLabel('app_name', 'apl_vv_operrreport')
    l6 = TextLabel('app_version', 'v1.0.1')
    m2.labels = [l4,l5,l6]
    m2.value = float(1)

#    h1 = Histogram('client_bucket', datetime.now(), 'Класс клиента - бедный, средний, богатый')
#    l7 = TextLabel('client_class', 'pure')
#    b1 = BucketLabel(100000)
#    h1.labels = [l7]
#    h1.buckets =[b1]
#    h1.value = 100
#
    with session:
        session.add(m1)
        session.add(m2)
#        session.add(h1)
        session.commit()

session = dal.Session()
prep_db(session)

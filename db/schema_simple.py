import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Table, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
import uuid

# CONNECTION_STRING = 'sqlite:///:memory:'
CONNECTION_STRING = 'sqlite:///db2prometheus'

engine = sqlalchemy.create_engine(CONNECTION_STRING)
Base = declarative_base()

import os


from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, MetaData, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import apl_naming_conventions as nc


Base = declarative_base()


metadata = MetaData(naming_convention=nc.db_objects_nc)

association_table = Table('association', metadata,
                           Column('id', Integer, primary_key=True),
                           Column('left_id', ForeignKey('left.id')),
                           Column('right_id', ForeignKey('right.id')),
                           Column('value', Float, nullable=False)
                           )




class Parent(Base):
    __tablename__ = 'left'
    metadata=metadata
    def __init__(self, name, children = []):
        self.name = name
        self.children = children

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    children = relationship("Child",
                            secondary=association_table)

class Child(Base):
    metadata=metadata
    __tablename__ = 'right'
    def __init__(self, name):
        self.name = name
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

#class Department(Base):
#    metadata=metadata
#    __tablename__ = 'department'
#    id = Column(Integer, primary_key=True)
#    name = Column(String)
#    employees = relationship(
#        'Employee',
#        secondary='department_employee_link'
#    )
#
#
#class Employee(Base):
#    metadata=metadata
#    __tablename__ = 'employee'
#    id = Column(Integer, primary_key=True)
#    name = Column(String)
#    hired_on = Column(DateTime, default=func.now())
#    departments = relationship(
#        Department,
#        secondary='department_employee_link'
#    )
#
#
#class DepartmentEmployeeLink(Base):
#    metadata=metadata
#    __tablename__ = 'department_employee_link'
#    department_id = Column(Integer, ForeignKey('department.id'), primary_key=True)
#    employee_id = Column(Integer, ForeignKey('employee.id'), primary_key=True)
#    extra_data = Column(String(256))
#    department = relationship(Department, backref=backref("employee_assoc"))
#    employee = relationship(Employee, backref=backref("department_assoc"))
#
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
    c1 =Child('c1')
    c2 =Child('c2')
    c3 =Child('c3')
    p1 =Parent(name='p1', children=[c1, c2, c3])
    p2 =Parent(name='p2', children=[c1, c2, c3])
    # c2 =Child(name = 'c2')
    # c3=Child(name = 'c3')
    # p1.children = [c1, c2, c3]
    # p2.children = [c3,c1]



    with session:
        session.add(p1)
        session.add(p2)
        session.commit()

session = dal.Session()
prep_db(session)
#prep_db(Session(dal.session).bulk_save_objects(m1))

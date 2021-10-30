from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase

Base = declarative_base()

class A(Base):
    __tablename__ = 'a'
    id = Column(Integer, primary_key=True)

class BC(Base):
    __tablename__ = 'bc'
    type = Column(String(50))
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity': 'bc','with_polymorphic': '*'}

class B(BC):
    __tablename__ = 'b'
    id = Column(Integer, primary_key=True)

    a_id = Column(Integer, ForeignKey('a.id'))
    __mapper_args__ = {
        "polymorphic_identity": "b",
        "concrete": True
    }

class C(BC):
    __tablename__ = 'c'
    id = Column(Integer, primary_key=True)
    a_id = Column(Integer, ForeignKey('a.id'))
    __mapper_args__ = {
        "polymorphic_identity": "c",
        "concrete": True
    }

configure_mappers()
A.collection = relationship(BC, primaryjoin=BC.a_id == A.id)

engine = create_engine("sqlite://", echo=True)

Base.metadata.create_all(engine)

sess = Session(engine)

sess.add_all([
    A(collection=[
        B(),
        C(),
        C()
    ]),
    A(collection=[
        B(),
        B()
    ])
])

sess.commit()

for a in sess.query(A):
    for bc in a.collection:
        print (a, bc)

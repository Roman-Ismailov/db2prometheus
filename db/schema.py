import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, text, Float
from sqlalchemy.orm import sessionmaker, relationship, backref, declarative_base
from sqlalchemy.future import select
# from sqlalchemy.ext.associationproxy import association_proxy
import uuid
import copy



engine = sqlalchemy.create_engine('sqlite:///manytomany.sqlite', future=True, echo=True)  # sqlalchemy 2.0 api
Base = declarative_base()


class MetricLabel(Base):
    __tablename__ = 'metrics_labels'
    # id = Column(String(35), primary_key=True, unique=True)
    # id = Column(Integer, primary_key=True, unique=True
    metric_id = Column(Integer, ForeignKey('metrics.id'), primary_key=True)
    label_id = Column(Integer, ForeignKey('labels.id'), primary_key=True)
    value = Column(Float)


    # metric_id = Column(Integer, ForeignKey('metrics.id'), primary_key=True)
    # label_id = Column(Integer, ForeignKey('labels.id'), primary_key=True)

    metric = relationship("Metric", backref=backref("metrics_labels", cascade="all, delete-orphan"))
    label = relationship("Label", backref=backref("metrics_labels", cascade="all, delete-orphan"))

    def __init__(self, metric=None, label=None, value=None):
        # self.id = uuid.uuid4().hex
        self.metric = metric
        self.label = label
        self.value = value

    def __repr__(self):
        return '<MetricLabels {}>'.format(self.metric.name+" "+self.label.name)


class Metric(Base):
    __tablename__ = 'metrics'
    # id = Column(String(35),  primary_key=True, unique=True)
    id = Column(Integer,  primary_key=True, unique=True)
    name = Column(String(80), nullable=False)
    labels = relationship("Label", secondary="metrics_labels", viewonly=True)

    def __init__(self, name):
        # self.id = uuid.uuid4().hex
        self.name = name
        self.orders = []

    def add_labels(self, items):
        for label, value in items:
            self.metrics_labels.append(MetricLabel(metric=self, label=label, value=value))

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Label(Base):
    __tablename__ = 'labels'
    # id = Column(String(35),  primary_key=True, unique=True)
    id = Column(Integer,  primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    metrics = relationship("Metric", secondary="metrics_labels", viewonly=True)

    def __key(self):
        return (self.name, self.value)

    def __hash__(self):
        return hash(self.__key())

    # compare only key val
    def __eq__(self, other):
        if isinstance(other, Label):
            return self.__key() == other.__key()
        return NotImplemented

    def __init__(self, name, value):
        # self.id = uuid.uuid4().hex
        self.name = name
        self.value = value
        self.metrics = []

    def __repr__(self):
        return '<Label {}>'.format(self.name)

class LabelsSet(Base):
    __tablename__='labels_sets'
    id = Column(Integer, nullable=False, primary_key=True, unique=True)
    hash = Column(String(64))
    _labels = set()

    def __key(self):
        x=''
        for l in self._labels:
            x = x+l.name+l.value
        return (x)

    def __hash__(self):
        print('DEBUG',self, self.__key())
        return (uuid.uuid5(uuid.NAMESPACE_DNS, self.__key()).hex)

    # compare only key val
    def __eq__(self, other):
        if isinstance(other, Label):
            return self.__key() == other.__key()
        return NotImplemented

    def __init__(self, labels=[]):
        self._labels = set()
        self.__update(labels)
        self.hash = self.__hash__()

    def sorted_list(self):
        return sorted(set(self._labels), key=lambda label: label.name.strip().upper()
                                                    +label.value.strip().upper())

    def __update(self, labels = []):

        # return NotImplemented
        v_labels  = copy.deepcopy(labels)
        for l in v_labels:
            l.name = l.name.upper().strip()
            l.value = l.value.upper().strip()
            if isinstance (self._labels, list):
                self._labels.append([l])
            else:
                self._labels.update([l])
            # self._labels = self._labels[:]
        self._labels = self.sorted_list()

        # print(self._labels)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()

l1 = Label(name="team",value= "Dream Team")
l2 = Label(name="version",value= "4.0")
l3 = Label(name="owner",value= "DRPA")
l4 = Label(name="version",value= "6.0")
l5 = Label(name="version",value= "5.0")
l6 = Label(name="version",value= "15.0")
l7 = Label(name="team",value= "pirates")
l8 = Label(name="team1",value= "pirates")

session.add_all([l1, l2, l3, l4, l5, l6, l7])
session.commit()

m1 = Metric(name="MyMetric")
m1.add_labels([(l1, 1.0), (l2, 1)])
# m1.labels=[l1, l2, l3, l4]
session.add(m1)
session.commit()


ls = list(session.execute(select(Label)).scalars().all())
ls1 = session.execute(select(Label).where(Label.name == 'a')).scalars().all()
print(ls)
print(ls1)
l = LabelsSet(ls)
lbls = LabelsSet(ls1)

print(l.__hash__(), lbls.__hash__())

l = LabelsSet([l1, l1, l2, l3, l4])
session.add(l)
session.commit()

for x in l._labels:
    print((x.name), x.value, 'adfdsf')
print(l.__hash__())
# l.update(set([l8]))
print(lbls.__hash__())

# print(l.__hash__())
# -2926104772848612253
#-7735740376372270998
#-898691598417870252
# print(l.__key__())
# print(sorted(oset, key = lambda label: label.name+label.value))


# order1 = Order( name = "First Order")
# order2 = Order( name = "Second Order")
#

# ###drop down

# class AbstractMetric( AbstractConcreteBase ):
#    # __mapper_args__ = {
#    #     'polymorphic_identity':'abstract_metric',
#    #     'polymorphic_on':'type'
#    # }
#    # id = Column(String(35), primary_key=True, unique=True)
#    # type = Column(String(50))
#    def __init__(self, name):
#        self.id = uuid.uuid5(uuid.NAMESPACE_DNS, name=name.upper() ).hex
#        #self.id = uuid.uuid4().hex
#        self.name = name.upper().strip()
#
#    id = Column(String(35),  primary_key=True, unique=True)
#    name = Column(String(64), nullable=False)
#    @declared_attr
#    def label_id(cls):
#        return Column(ForeignKey('abstract_labels.id'))
#    @declared_attr
#    def labels(cls):
#        return relationship("AbstractLabel")
#        # if type(cls).name == 'TextLabel':
#        #     return relationship("TextLabel", secondary="text_labels", viewonly=True)
#    #pass
#
# class Gauge(AbstractMetric):
#    __tablename__ = 'gauge_metrics'
#    value = Column(Float, nullable=False)
#    label_id = Column(Integer, ForeignKey('text_labels.id'), primary_key=True)
#    def __init__(self, name, value, labels = []):
#        self.value = value
#        # self.labels =[]
#        super(Gauge, self).__init__(name)
#    __mapper_args__ = {
#        'polymorphic_identity':'gauge',
#        'concrete':True
#    }
#
#class AbstractLabel(AbstractConcreteBase, Base):
#    def __init__(self, name):
#        self.id = uuid.uuid4().hex
#        self.name = name
#    id = Column(String(35),  primary_key=True, unique=True)
#    name = Column(String(64), nullable=False)
#
#class TextLabel(AbstractLabel):
#    __tablename__ = 'text_labels'
#    value = Column(String(64), nullable=False)
#    def __init__(self, name, value, metric):
#        self.name = name
#        self.value = value
#        super(TextLabel, self).__init__(name)
#
#    __mapper_args__ = {
#        'polymorphic_identity':'text_label',
#        'concrete':True
#    }
#
#
#class Histogram(AbstractMetric):
#    __tablename__ = 'histogram_metrics'
#    value = Column(Float, nullable=False)
#    __mapper_args__ = {
#        'polymorphic_identity':'histogram',
#        'concrete':True
#    }
#configure_mappers()
#
#
#
#
#class Order_Product(Base):
#    __tablename__ = 'order_product'
#    id = Column(String(35), primary_key=True, unique=True)
#    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
#    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
#    quantity = Column(Integer)
#
#    order = relationship("Order", backref=backref("order_products", cascade="all, delete-orphan" ))
#    product = relationship("Product", backref=backref("order_products", cascade="all, delete-orphan" ))
#
#    def __init__(self, order=None, product=None, quantity=None):
#        self.id = uuid.uuid4().hex
#        self.order = order
#        self.product =  product
#        self.quantity = quantity
#
#    def __repr__(self):
#        return '<Order_Product {}>'.format(self.order.name+" "+self.product.name)
#
#class Product(Base):
#    __tablename__ = 'products'
#    id = Column(String(35),  primary_key=True, unique=True)
#    name = Column(String(80), nullable=False)
#
#    orders = relationship("Order", secondary="order_product", viewonly=True)
#
#    def __init__(self, name):
#        self.id = uuid.uuid4().hex
#        self.name = name
#        self.orders=[]
#
#    def __repr__(self):
#        return '<Product {}>'.format(self.name)
#
#
#class Order(Base):
#    __tablename__ = 'orders'
#    id = Column(String(35),  primary_key=True, unique=True)
#    name = Column(String(80), nullable=False)
#
#    products = relationship("Product", secondary="order_product", viewonly=True)
#
#    def add_products(self, items):
#        for product, qty in items:
#            self.order_products.append(Order_Product(order=self, product=product, quantity=qty))
#
#
#
#
#    def __init__(self, name):
#        self.id = uuid.uuid4().hex
#        self.name = name
#        self.products =[]
#
#    def __repr__(self):
#        return '<Order {}>'.format(self.name)
#
#
#Base.metadata.drop_all(engine)
#Base.metadata.create_all(engine)
#
#Session = sessionmaker(bind=engine)
#session = Session()
#
#prod1 = Product(name="Oreo")
#prod2 = Product(name="Hide and Seek")
#prod3 = Product(name="Marie")
#prod4 = Product(name="Good Day")
#
#
#session.add_all([prod1, prod2, prod3, prod4])
#session.commit()
#
#order1 = Order( name = "First Order")
#order2 = Order( name = "Second Order")
#
#gauge1 = Gauge(name = 'gini', value = 1.23)
## text_label1 = TextLabel(name = 'team_name', value = 'apl_products', metric = gauge1)
#
#session.add(gauge1)
## session.add(text_label1)
#
#
#order1.add_products([ (prod1,4) , (prod2,5) , (prod3,4) ])
#order2.add_products([ (prod2,6) , (prod1,1) , (prod3,2), (prod4,1) ])
#
#session.commit()
#
#
#print( "Products array of order1: ")
#print( order1.products)
#print( "Products array of order2: ")
#print( order2.products)
#print( "Orders array of prod1: ")
#print( prod1.orders)
#print( "Orders array of prod2: ")
#print( prod2.orders)
#print( "Orders array of prod3: ")
#print( prod3.orders)
#print( "Orders array of prod4: ")
#print( prod4.orders)
#
#print( "Order_Products Array of order1 : ")
#print( order1.order_products)
#
#print( "Order_Products Array of prod1 : ")
#print( prod1.order_products)

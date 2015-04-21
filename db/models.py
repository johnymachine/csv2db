from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Mesurement(Base):
    __tablename__ = 'mesurement'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    value1 = Column(Float)
    value2 = Column(Float)

    unit = Column(Integer, ForeignKey('unit.unit'))
    block_id = Column(Integer, ForeignKey('block.id'))
    device_sn = Column(Integer, ForeignKey('device.serial_num'))
    location_id = Column(Integer, ForeignKey('location.id'))


class Unit(Base):
    __tablename__ = 'unit'

    unit = Column(String(30), primary_key=True)
    deviation = Column(Float, nullable=False, default=0)

    mesurements = relationship('Mesurement', backref='unit')


class Block(Base):
    __tablename__ = 'block'

    id = Column(Integer, primary_key=True)
    description = Column(String(300))

    mesurements = relationship('Mesurement', backref='block')


class Device(Base):
    __tablename__ = 'device'

    serial_num = Column(String(80), primary_key=True)
    deviation = Column(Float, nullable=False, default=0)
    description = Column(String(300))

    mesurements = relationship('Mesurement', backref='device')


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, Sequence('location_id_seq'), primary_key=True)
    longtitute = Column(Float, nullable=False)
    latitute = Column(Float, nullable=False)

    mesurements = relationship('Mesurement', backref='location')

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, Float, DateTime
from sqlalchemy.orm import relation

from database import Base


class OptionTable(Base):
    __tablename__ = 'option'
    id = Column(Integer, primary_key=True)
    value = Column(String(80), nullable=False)
    order = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("variable.id"))

    variable = relation('VariableTable')


class VariableTable(Base):
    __tablename__ = 'variable'
    id = Column(String(64), primary_key=True)
    question = Column(String(128), unique=True, nullable=False)
    is_scalar = Column(Boolean, nullable=False, default=False)

    options = relation(OptionTable, overlaps="variable")


premise = Table(
    'premise',
    Base.metadata,
    Column('option_id', ForeignKey('option.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False),
)

conclusion = Table(
    'conclusion',
    Base.metadata,
    Column('option_id', ForeignKey('option.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False)
)


class RuleTable(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    formula = Column(String(256))

    premises = relation(OptionTable, secondary=premise)
    conclusions = relation(OptionTable, secondary=conclusion)


class ClientTable(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    last_name = Column(String(32), nullable=False)
    phone_number = Column(String(16))
    email = Column(String(64))


class SelectedOptionTable(Base):
    __tablename__ = 'selected_option'
    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)
    scalar = Column(String(32))
    quotation_id = Column(Integer, ForeignKey("quotation.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("option.id"), nullable=False)


class SelectedDeviceTable(Base):
    __tablename__ = 'selected_device'
    id = Column(Integer, primary_key=True)
    usage_time = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    quotation_id = Column(Integer, ForeignKey("quotation.id"), nullable=False)


class QuotationTable(Base):
    __tablename__ = 'quotation'
    id = Column(Integer, primary_key=True)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.now)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

    selected_options = relation(SelectedOptionTable)
    selected_devices = relation(SelectedDeviceTable)
    client = relation(ClientTable)


class DeviceTable(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    category = Column(String(32), nullable=False)
    rated_power = Column(Float, nullable=False)
    bootstrap_factor = Column(Float, nullable=False)
    actual_power = Column(Float, nullable=False)

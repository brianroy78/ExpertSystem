from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relation

from database import Base


class ValueTable(Base):
    __tablename__ = 'value'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    order = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("variable.id"))

    variable = relation('VariableTable')


class VariableTable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    options = relation(ValueTable, overlaps="variable")


premise = Table(
    'premise',
    Base.metadata,
    Column('value_id', ForeignKey('value.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False),
)

conclusion = Table(
    'conclusion',
    Base.metadata,
    Column('value_id', ForeignKey('value.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False),
)


class RuleTable(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)

    premises = relation(ValueTable, secondary=premise)
    conclusions = relation(ValueTable, secondary=conclusion)


class ClientTable(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    last_name = Column(String(32), nullable=False)
    phone_number = Column(String(16))
    email = Column(String(64))


selected_options = Table(
    'selected_options',
    Base.metadata,
    Column('value_id', ForeignKey('value.id'), nullable=False),
    Column('inference_id', ForeignKey('inference.id'), nullable=False),
)


class InferenceTable(Base):
    __tablename__ = 'inference'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

    selected_options = relation(ValueTable, secondary=selected_options)

    client = relation(ClientTable)

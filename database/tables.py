from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relation

from database import Base


class ValueTable(Base):
    __tablename__ = 'value'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    parent_id = Column(Integer, ForeignKey("variable.id"))


class VariableTable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    required = Column(Boolean, nullable=False, default=False)

    options = relation(ValueTable)


class FactTable(Base):
    __tablename__ = 'fact'
    id = Column(Integer, primary_key=True)
    variable_id = Column(Integer, ForeignKey('variable.id'), nullable=False)
    value_id = Column(Integer, ForeignKey('value.id'), nullable=False)

    variable = relation(VariableTable)
    value = relation(ValueTable)


premise = Table(
    'premise',
    Base.metadata,
    Column('fact_id', ForeignKey('fact.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False),
)

conclusion = Table(
    'conclusion',
    Base.metadata,
    Column('fact_id', ForeignKey('fact.id'), nullable=False),
    Column('rule_id', ForeignKey('rule.id'), nullable=False),
)


class RuleTable(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)

    premises = relation(FactTable, secondary=premise)
    conclusions = relation(FactTable, secondary=conclusion)


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
    Column('fact_id', ForeignKey('fact.id'), nullable=False),
    Column('inference_id', ForeignKey('inference.id'), nullable=False),
)


class InferenceTable(Base):
    __tablename__ = 'inference'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)

    selected_options = relation(FactTable, secondary=selected_options)

    client = relation(ClientTable)

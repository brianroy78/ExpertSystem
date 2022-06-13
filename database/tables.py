from sqlalchemy import Column, Integer, String, ForeignKey, Table
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

    options = relation(ValueTable)


rules_facts = Table(
    "rule_fact",
    Base.metadata,
    Column("fact_id", ForeignKey("fact.id")),
    Column("rule_id", ForeignKey("rule.id")),
)


class FactTable(Base):
    __tablename__ = 'fact'
    id = Column(Integer, primary_key=True)
    variable_id = Column(Integer, ForeignKey('variable.id'))
    value_id = Column(Integer, ForeignKey('value.id'))

    variable = relation(VariableTable)
    value = relation(ValueTable)
    rules = relation('RuleTable', secondary=rules_facts)


class RuleTable(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey('fact.id'))

    statement = relation(FactTable)
    premises = relation(FactTable, secondary=rules_facts)

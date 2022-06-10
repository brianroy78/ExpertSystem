from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relation

from database import Base


class Value(Base):
    __tablename__ = 'value'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("variable.id"))


class Variable(Base):
    __tablename__ = 'variable'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    options = relation(Value)


rules_facts = Table(
    "rule_fact",
    Base.metadata,
    Column("fact_id", ForeignKey("fact.id")),
    Column("rule_id", ForeignKey("rule.id")),
)


class Fact(Base):
    __tablename__ = 'fact'
    id = Column(Integer, primary_key=True)
    variable_id = Column(Integer, ForeignKey('variable.id'))
    value_id = Column(Integer, ForeignKey('value.id'))

    variable = relation(Variable)
    value = relation(Value)
    rules = relation('Rule', secondary=rules_facts)


class Rule(Base):
    __tablename__ = 'rule'
    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey('fact.id'))

    premises = relation(Fact, secondary=rules_facts)

from dataclasses import dataclass
from typing import FrozenSet, Set


@dataclass(frozen=True, eq=True)
class Value:
    id: int
    name: str
    # Variable: 'Variable'


@dataclass(frozen=True, eq=True)
class Variable:
    id: int
    name: str
    options: FrozenSet[Value]


@dataclass(frozen=True, eq=True)
class Fact:
    variable: Variable
    value: Value


@dataclass
class Rule:
    premises: Set[Fact]
    statement: Fact

    def __repr__(self):
        r = [f'{p.variable.name} -> {p.value.name}' for p in self.premises]
        return f'{",".join(r)} ==> {self.statement.variable.name} -> {self.statement.value.name}'


@dataclass
class Inference:
    rules: Set[Rule]
    facts: Set[Fact]

from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True, eq=True)
class Value:
    id: int
    name: str
    order: int


@dataclass(frozen=True, eq=True)
class Variable:
    id: int
    name: str
    options: FrozenSet[Value]


@dataclass(frozen=True, eq=True)
class Fact:
    variable: Variable
    value: Value


@dataclass(frozen=True, eq=True)
class Rule:
    premises: FrozenSet[Fact]
    conclusions: FrozenSet[Fact]

    def __repr__(self):
        premises = [f'{p.variable.name} -> {p.value.name}' for p in self.premises]
        conclusions = [f'{c.variable.name} -> {c.value.name}' for c in self.conclusions]
        return f'{",".join(premises)} ==> {",".join(conclusions)}'


@dataclass
class Inference:
    rules: set[Rule]
    facts: set[Fact]
    ignored_variables: set[Variable]
    current_variable: Variable
    is_finished: bool


@dataclass
class Pair:
    rules: set[Rule]
    facts: set[Fact]

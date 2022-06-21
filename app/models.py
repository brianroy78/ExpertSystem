from dataclasses import dataclass


@dataclass
class Option:
    value: str
    order: int
    variable: 'Variable'

    def __hash__(self):
        return hash((self.value, self.variable.name))

    def __eq__(self, other: object):
        if not isinstance(other, Option):
            raise NotImplementedError()
        return self.value == other.value and self.variable == other.variable


@dataclass
class Variable:
    name: str
    options: set[Option]
    is_scalar: bool

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: object):
        if not isinstance(other, Variable):
            raise NotImplementedError()
        return self.name == other.name


@dataclass
class Rule:
    premises: set[Option]
    conclusions: set[Option]

    def __hash__(self):
        return hash((tuple(self.premises), tuple(self.conclusions)))

    def __eq__(self, other):
        if not isinstance(other, Rule):
            raise NotImplementedError()
        return tuple(self.premises) == tuple(other.premises) and tuple(self.conclusions) == tuple(other.conclusions)

    def __repr__(self):
        premises = [f'{p.variable.name} -> {p.value}' for p in self.premises]
        conclusions = [f'{c.variable.name} -> {c.value}' for c in self.conclusions]
        return f'{",".join(premises)} ==> {",".join(conclusions)}'


@dataclass
class Inference:
    rules: set[Rule]
    facts: set[Option]
    vars: list[Variable]


Premises = set[Option]
Conclusions = set[Option]
Variables = set[Variable]

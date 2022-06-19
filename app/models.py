from dataclasses import dataclass


@dataclass
class Value:
    name: str
    order: int
    variable: 'Variable'

    def __hash__(self):
        return hash((self.name, self.variable.name))

    def __eq__(self, other: object):
        if not isinstance(other, Value):
            raise NotImplementedError()
        return self.name == other.name and self.variable == other.variable


@dataclass
class Variable:
    name: str
    options: set[Value]

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: object):
        if not isinstance(other, Variable):
            raise NotImplementedError()
        return self.name == other.name


@dataclass
class Rule:
    premises: set[Value]
    conclusions: set[Value]

    def __hash__(self):
        return hash((tuple(self.premises), tuple(self.conclusions)))

    def __eq__(self, other):
        if not isinstance(other, Rule):
            raise NotImplementedError()
        return tuple(self.premises) == tuple(other.premises) and tuple(self.conclusions) == tuple(other.conclusions)

    def __repr__(self):
        premises = [f'{p.variable.name} -> {p.name}' for p in self.premises]
        conclusions = [f'{c.variable.name} -> {c.name}' for c in self.conclusions]
        return f'{",".join(premises)} ==> {",".join(conclusions)}'


@dataclass
class Inference:
    rules: set[Rule]
    facts: set[Value]
    vars: list[Variable]


Premises = set[Value]
Conclusions = set[Value]
Variables = set[Variable]

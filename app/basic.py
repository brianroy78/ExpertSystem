from functools import partial
from typing import Iterable

from app.custom_functions import reduce_ior
from app.models import Variable, Rule, Conclusions, Variables, Option


def get_variable(value: Option) -> Variable:
    return value.variable


def get_conclusions(rule: Rule) -> Conclusions:
    return rule.conclusions


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def get_premises_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.premises))


def get_conclusions_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.conclusions))


# copy

def duplicate_rule(rule: Rule) -> Rule:
    return Rule(set(rule.premises), set(rule.conclusions))


# contains

def premises_contains_variable(variable: Variable, rule: Rule) -> bool:
    return variable in get_premises_variables(rule)


def conclusions_contains_variable(variable: Variable, rule: Rule) -> bool:
    return variable in get_conclusions_variables(rule)


# filters

def filter_variable_in_premises(rules: set[Rule], variable: Variable) -> Iterable[Rule]:
    return filter(partial(premises_contains_variable, variable), rules)


def filter_variable_in_conclusions(rules: set[Rule], variable: Variable) -> Iterable[Rule]:
    return filter(partial(conclusions_contains_variable, variable), rules)


# graph

def get_fathers_by_rules(rules: set[Rule], variable: Variable) -> Iterable[Variable]:
    return reduce_ior(map(get_conclusions_variables, filter_variable_in_premises(rules, variable)))


def get_children_by_rules(rules: set[Rule], variable: Variable) -> Iterable[Variable]:
    return reduce_ior(map(get_premises_variables, filter_variable_in_conclusions(rules, variable)))

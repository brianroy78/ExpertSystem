from functools import partial
from typing import Iterable

from app.custom_functions import reduce_or
from app.models import Variable, Rule, Conclusions, Variables, Option, Inference


def get_variable_id(variable: Variable) -> str:
    return variable.id


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

def copy_option(option: Option) -> Option:
    return Option(option.id, option.value, option.scalar, option.order, option.variable)


def copy_rule(rule: Rule) -> Rule:
    return Rule(set(rule.premises), set(rule.conclusions), rule.formula)


def copy_inference(inference: Inference) -> Inference:
    return Inference(
        set(map(copy_rule, inference.rules)),
        set(map(copy_option, inference.facts)),
        list(inference.vars),
        inference.quotation_id
    )


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

def get_children_by_rules(rules: set[Rule], variable: Variable) -> Iterable[Variable]:
    return reduce_or(map(get_conclusions_variables, filter_variable_in_premises(rules, variable)))


def get_parents_by_rules(rules: set[Rule], variable: Variable) -> Iterable[Variable]:
    return reduce_or(map(get_premises_variables, filter_variable_in_conclusions(rules, variable)))

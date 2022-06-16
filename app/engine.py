from functools import reduce, partial
from operator import ior
from typing import Iterable

from app.models import Rule, Variable, Fact
from app.utils import first, group_by, remove_from_frozen, compose


def get_variable(fact: Fact) -> Variable:
    return fact.variable


def get_conclusions(rule: Rule) -> frozenset[Fact]:
    return rule.conclusions


def get_variables(rule: Rule) -> set[Variable]:
    return set(map(get_variable, rule.premises))


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def update_rule(fact: Fact, rule: Rule) -> Rule:
    clone: Rule = rule
    if fact in clone.premises:
        clone = Rule(remove_from_frozen(clone.premises, fact), clone.conclusions)
    if fact in clone.conclusions:
        clone = Rule(clone.premises, remove_from_frozen(clone.conclusions, fact))
    return clone


def is_ruled_out(fact: Fact, rule: Rule) -> bool:
    if len(rule.conclusions) == 1 and fact.variable == first(rule.conclusions).variable:
        return False
    return fact.variable not in get_variables(rule) or fact in rule.premises


def _infer(rules: list[Rule], fact: Fact) -> tuple[list[Rule], set[Fact]]:
    result: dict[bool, list[Rule]] = compose(
        partial(filter, partial(is_ruled_out, fact)),
        partial(map, partial(update_rule, fact)),
        partial(group_by, premises_empty)
    )(rules)
    new_facts: Iterable[frozenset[Fact]] = map(get_conclusions, result.get(True, list()))
    return result.get(False, list()), reduce(ior, new_facts, set())


def infer(rules: set[Rule], fact: Fact) -> tuple[list[Rule], set[Fact]]:
    facts = {fact}
    result_facts = {fact}
    result_rules = list(rules)
    while len(facts) > 0 and len(result_rules) > 0:
        result_rules, new_facts = _infer(result_rules, facts.pop())
        facts |= new_facts
        result_facts |= new_facts
    return result_rules, result_facts

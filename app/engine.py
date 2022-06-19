from functools import partial
from typing import Iterable

from app.basic import get_conclusions, get_premises_variables, premises_empty
from app.custom_functions import reduce_ior
from app.models import Rule, Value
from app.utils import first, group_by, compose


def update_rule(fact: Value, rule: Rule) -> Rule:
    clone: Rule = rule
    if fact in clone.premises:
        clone = Rule(clone.premises - {fact}, clone.conclusions)
    if fact in clone.conclusions:
        clone = Rule(clone.premises, clone.conclusions - {fact})
    return clone


def is_ruled_out(fact: Value, rule: Rule) -> bool:
    if len(rule.conclusions) == 1 and fact.variable == first(rule.conclusions).variable:
        return False
    return fact.variable not in get_premises_variables(rule) or fact in rule.premises


def _infer(rules: set[Rule], fact: Value) -> tuple[set[Rule], set[Value]]:
    result: dict[bool, list[Rule]] = compose(
        partial(filter, partial(is_ruled_out, fact)),
        partial(map, partial(update_rule, fact)),
        partial(group_by, premises_empty)
    )(rules)
    new_facts: Iterable[set[Value]] = map(get_conclusions, result.get(True, list()))
    return set(result.get(False, set())), reduce_ior(new_facts)


def infer(rules: set[Rule], fact: Value) -> tuple[set[Rule], set[Value]]:
    input_facts = {fact}
    result_facts = {fact}
    result_rules = set(rules)
    while len(input_facts) > 0 and len(result_rules) > 0:
        result_rules, new_facts = _infer(result_rules, input_facts.pop())
        input_facts |= new_facts
        result_facts |= new_facts

    return result_rules, result_facts

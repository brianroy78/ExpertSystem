from itertools import groupby
from typing import Set, Tuple, List, Iterable, Dict, Callable

from app.models import Rule, Variable, Fact
from app.utils import LF


def curry(function: Callable, param) -> Callable:
    def new_func(*args):
        return function(param, *args)

    return new_func


def get_variable(fact: Fact) -> Variable:
    return fact.variable


def get_statement(rule: Rule) -> Fact:
    return rule.statement


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def get_variables(rule: Rule) -> Set[Variable]:
    return set(map(get_variable, rule.premises))


def group_by(key: Callable, iterable: Iterable) -> Dict:
    result = dict()
    for key, groups in groupby(iterable, key):
        if key not in result:
            result[key] = list()
        result[key].extend(list(groups))
    return result


def update_rule_base_on_fact(fact: Fact, rule: Rule) -> Rule:
    if fact in rule.premises:
        rule.premises.remove(fact)
    return rule


def purge_rule_base_on_fact(fact: Fact, rule: Rule) -> bool:
    if fact.variable == rule.statement.variable:
        return False
    return fact.variable not in get_variables(rule) or fact in rule.premises


def _infer(rules: List[Rule], fact: Fact) -> Tuple[List[Rule], Set[Fact]]:
    update_rule: Callable[[Rule], Rule] = curry(update_rule_base_on_fact, fact)
    purge_rule: Callable[[Rule], bool] = curry(purge_rule_base_on_fact, fact)
    result: Dict[bool, List[Rule]] = group_by(premises_empty, LF(rules).filter(purge_rule).map(update_rule).value)
    new_facts = LF(result.get(True, list())).map(get_statement).value
    return result.get(False, list()), set(new_facts)


def infer(rules: List[Rule], fact: Fact) -> Tuple[List[Rule], Set[Fact]]:
    facts = {fact}
    result_facts = {fact}
    result_rules = list(rules)
    while len(facts) > 0 and len(result_rules) > 0:
        result_rules, new_facts = _infer(result_rules, facts.pop())
        facts |= new_facts
        result_facts |= new_facts
    return result_rules, result_facts

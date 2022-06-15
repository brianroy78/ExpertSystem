from functools import reduce
from itertools import groupby
from operator import ior
from typing import Set, Tuple, List, Iterable, Dict, Callable, FrozenSet

from app.models import Rule, Variable, Fact
from app.utils import LF


def curry(function: Callable, param) -> Callable:
    def new_func(*args):
        return function(param, *args)

    return new_func


def first(elements: FrozenSet):
    return next(iter(elements))


def get_variable(fact: Fact) -> Variable:
    return fact.variable


def get_conclusions(rule: Rule) -> FrozenSet[Fact]:
    return rule.conclusions


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def get_variables(rule: Rule) -> Set[Variable]:
    return set(map(get_variable, rule.premises))


def remove_fact(facts: FrozenSet[Fact], fact: Fact) -> FrozenSet[Fact]:
    facts_: Set[Fact] = set(facts)
    facts_.remove(fact)
    return frozenset(facts_)


def group_by(key: Callable, iterable: Iterable) -> Dict:
    result = dict()
    for key, groups in groupby(iterable, key):
        if key not in result:
            result[key] = list()
        result[key].extend(list(groups))
    return result


def update_rule_base_on_fact(fact: Fact, rule: Rule) -> Rule:
    clone: Rule = rule
    if fact in clone.premises:
        clone = Rule(remove_fact(clone.premises, fact), clone.conclusions)
    if fact in clone.conclusions:
        clone = Rule(clone.premises, remove_fact(clone.conclusions, fact))
    return clone


def purge_rule_base_on_fact(fact: Fact, rule: Rule) -> bool:
    if len(rule.conclusions) == 1 and fact.variable == first(rule.conclusions).variable:
        return False
    return fact.variable not in get_variables(rule) or fact in rule.premises


def _infer(rules: List[Rule], fact: Fact) -> Tuple[List[Rule], Set[Fact]]:
    update_rule: Callable[[Rule], Rule] = curry(update_rule_base_on_fact, fact)
    purge_rule: Callable[[Rule], bool] = curry(purge_rule_base_on_fact, fact)
    group_by_empty_premises: Callable[[Iterable[Rule]], Dict[bool, List[Rule]]] = curry(group_by, premises_empty)

    result: Dict[bool, List[Rule]] = LF(rules). \
        filter(purge_rule). \
        map(update_rule). \
        apply(group_by_empty_premises).value
    # result: Dict[bool, List[Rule]] = group_by(premises_empty, LF(rules).filter(purge_rule).map(update_rule).value)
    triggered_rules: List[Rule] = result.get(True, list())
    new_facts: Iterable[Set[Fact]] = LF(triggered_rules).map(get_conclusions).map(set).value
    result_facts: Set[Fact] = reduce(ior, new_facts, set())
    return result.get(False, list()), set(result_facts)


def infer(rules: List[Rule], fact: Fact) -> Tuple[List[Rule], Set[Fact]]:
    facts = {fact}
    result_facts = {fact}
    result_rules = list(rules)
    while len(facts) > 0 and len(result_rules) > 0:
        result_rules, new_facts = _infer(result_rules, facts.pop())
        facts |= new_facts
        result_facts |= new_facts
    return result_rules, result_facts

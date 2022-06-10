from typing import List, Tuple, Set

from engine import get_variable
from models import Rule, Fact, Variable


def _infer(rules: List[Rule], fact: Fact) -> Tuple[List[Rule], Set[Fact]]:
    result_rules: List[Rule] = list()
    result_facts: Set[Fact] = set()
    for rule in list(rules):
        if fact in rule.premises:
            rule.premises.remove(fact)
            if len(rule.premises) == 0:
                result_facts.add(rule.statement)
                continue
            result_rules.append(rule)
            continue

        proposed_variables: Set[Variable] = set(map(get_variable, rule.premises))
        if fact.variable in proposed_variables and fact not in rule.premises:
            continue
        result_rules.append(rule)

    return result_rules, result_facts
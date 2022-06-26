from functools import partial
from typing import Iterable

from app.basic import get_conclusions, get_premises_variables, premises_empty, clone_rule
from app.custom_functions import reduce_or
from app.models import Rule, Option
from app.utils import first, group_by, compose


def trigger_rule(rule: Rule) -> set[Option]:
    if rule.formula is None:
        return get_conclusions(rule)
    result: dict = {}
    exec(f'result={rule.formula}', result)
    conclusion: Option = rule.conclusions.pop()
    if conclusion.variable.is_scalar:
        conclusion.scalar = result['result']
    else:
        conclusion.value = result['result']
    return {conclusion}


def update_rule(fact: Option, rule: Rule) -> Rule:
    clone: Rule = clone_rule(rule)
    if clone.formula is not None and fact.variable in get_premises_variables(clone):
        clone.formula = clone.formula.replace(fact.variable.id, str(fact.scalar))
    if fact in clone.premises:
        clone.premises -= {fact}
    if fact in clone.conclusions:
        clone.conclusions -= {fact}
    return clone


# alternate implementation:
# if fact's variable in conclusion's variable and fact not in conclusion
# rule out!
def is_ruled_out(fact: Option, rule: Rule) -> bool:
    if len(rule.conclusions) == 1 and fact.variable == first(rule.conclusions).variable:
        return False
    return fact.variable not in get_premises_variables(rule) or fact in rule.premises


def _infer(rules: set[Rule], fact: Option) -> tuple[set[Rule], set[Option]]:
    result: dict[bool, list[Rule]] = compose(
        partial(filter, partial(is_ruled_out, fact)),
        partial(map, partial(update_rule, fact)),
        partial(group_by, premises_empty)
    )(rules)
    new_facts: Iterable[set[Option]] = map(trigger_rule, result.get(True, set()))
    return set(result.get(False, set())), reduce_or(new_facts)


def infer(rules: set[Rule], fact: Option) -> tuple[set[Rule], set[Option]]:
    input_facts = {fact}
    result_facts = {fact}
    result_rules = set(rules)
    while len(input_facts) > 0 and len(result_rules) > 0:
        result_rules, new_facts = _infer(result_rules, input_facts.pop())
        input_facts |= new_facts
        result_facts |= new_facts

    return result_rules, result_facts

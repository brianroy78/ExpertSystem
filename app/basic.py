from app.models import Fact, Variable, Rule, Conclusions, Variables


def get_variable(fact: Fact) -> Variable:
    return fact.variable


def get_conclusions(rule: Rule) -> Conclusions:
    return rule.conclusions


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def get_premises_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.premises))


def get_conclusions_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.conclusions))

from app.models import Variable, Rule, Conclusions, Variables, Value


def get_variable(value: Value) -> Variable:
    return value.variable


def get_conclusions(rule: Rule) -> Conclusions:
    return rule.conclusions


def premises_empty(rule: Rule) -> bool:
    return len(rule.premises) == 0


def get_premises_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.premises))


def get_conclusions_variables(rule: Rule) -> Variables:
    return set(map(get_variable, rule.conclusions))

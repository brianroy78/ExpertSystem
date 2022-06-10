from typing import Set, List, Optional

from base import get_rules
from engine import infer
from models import Fact, Rule, Variable, Value


def present_var(variable: Variable) -> Optional[Value]:
    print(f'{variable.name}?')
    options: dict = {}
    for index, option in enumerate(variable.options):
        print(f'({index}) {option.name}')
        options[index] = option

    return options.get(int(input('respuesta: ')), None)


def has_ignored_var(rule: Rule, ignored_vars: Set[Variable]) -> bool:
    for premise in rule.premises:
        if premise.variable in ignored_vars:
            return True
    return False


def main():
    facts: Set[Fact] = set()
    rules: List[Rule] = get_rules()
    ignored_vars: Set[Variable] = set()
    ignored_rules: Set[Rule] = set()
    while len(rules) > 0:
        rule: Rule = rules[-1]
        if has_ignored_var(rule, ignored_vars):
            ignored_rules.add(rules.pop())
            continue
        for premise in set(rule.premises):
            variable: Variable = premise.variable
            actual_value = present_var(variable)
            if actual_value is None:
                ignored_vars.add(variable)
                ignored_rules.add(rules.pop())
                break
            actual_fact = Fact(variable, actual_value)
            rules, new_facts = infer(rules, actual_fact)
            facts |= new_facts

    print('----- resultados -----')
    for f in facts:
        print(f'{f.variable.name} => {f.value.name}')


if __name__ == '__main__':
    main()


def conventional():
    facts: Set[Fact] = set()
    rules: List[Rule] = get_rules()

    while True:
        rule = rules.pop()

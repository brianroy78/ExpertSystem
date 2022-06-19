from functools import reduce, partial
from operator import iconcat
from typing import Iterable, Callable, Optional

from app.basic import get_premises_variables, get_conclusions_variables
from app.custom_functions import reduce_ior
from app.models import Variable, Value, Rule
from database import get_session
from database.tables import VariableTable, ValueTable, RuleTable


def to_variable(variable_table: VariableTable, values: dict[int, Value]) -> Variable:
    variable = Variable(variable_table.name, set())
    for value_table in variable_table.options:
        value = values[value_table.id]
        value.variable = variable
        variable.options.add(value)

    return variable


def premises_contains_variable(variable: Variable, rule: Rule) -> bool:
    return variable in get_premises_variables(rule)


def filter_variable_in_rules_premises(rules: set[Rule], variable: Variable) -> Iterable[Rule]:
    return filter(partial(premises_contains_variable, variable), rules)


def variables_to_rules(variables: set[Variable], rules: set[Rule]) -> Iterable[Iterable[Rule]]:
    return map(partial(filter_variable_in_rules_premises, rules), variables)


def get_roots_by_rules(rules: set[Rule], variable: Variable) -> set[Variable]:
    target_variables: set[Variable] = {variable}
    clone_rules = set(rules)
    while True:
        rules_to_follow: list[Rule] = reduce(iconcat, variables_to_rules(target_variables, clone_rules), list())
        if len(rules_to_follow) == 0:
            return target_variables
        target_variables = reduce_ior(map(get_conclusions_variables, rules_to_follow))


var_list = list[tuple[int, Variable]]
vars_list = list[var_list]


def get_lvl(tuple_: tuple) -> int:
    return tuple_[0]


def from_table_to_model() -> tuple[set[Rule], list[Variable]]:
    with get_session() as session:
        stub_var = Variable('', set())
        values: dict[int, Value] = {v.id: Value(v.name, v.order, stub_var) for v in session.query(ValueTable)}
        variables: dict[int, Variable] = {v.id: to_variable(v, values) for v in session.query(VariableTable)}
        rules: set[Rule] = {
            Rule(
                set([values[p.id] for p in r.premises]),
                set([values[c.id] for c in r.conclusions])
            )
            for r in session.query(RuleTable)
        }
        get_roots: Callable[[Variable], set[Variable]] = partial(get_roots_by_rules, rules)
        roots: set[Variable] = reduce_ior(map(get_roots, variables.values()))
        walk: Callable[[Variable], var_list] = partial(walk_by_lvl, partial(get_children_by_rules, rules))
        variables_with_lvl: vars_list = list(map(walk, roots))
        ordered_by_deep: vars_list = sorted(variables_with_lvl, key=len, reverse=True)
        order_variables_set: Callable[[var_list], var_list] = partial(sorted, key=lambda o: o[0], reverse=True)
        ordered_by_lvl: vars_list = list(map(order_variables_set, ordered_by_deep))
        flatted: var_list = reduce(iconcat, ordered_by_lvl, list())
        return rules, list(map(lambda e: e[1], flatted))


def conclusions_contains_variable(variable: Variable, rule: Rule) -> bool:
    return variable in get_conclusions_variables(rule)


def get_children_by_rules(rules: set[Rule], variable: Variable) -> list[Variable]:
    children_rules: list[Rule] = list(filter(partial(conclusions_contains_variable, variable), rules))
    if len(children_rules) == 0:
        return []
    return list(reduce_ior(map(get_premises_variables, children_rules)))


def walk_by_lvl(get_children: Callable[[Variable], list[Variable]], root: Variable) -> list[tuple[int, Variable]]:
    result: list[tuple[int, Variable]] = []
    input_: list[tuple[int, Optional[Variable]]] = [(0, root)]
    while len(input_) > 0:
        lvl, node = input_.pop(0)
        if node is None:
            continue
        result.append((lvl, node))
        input_.extend(map(lambda n: (lvl + 1, n), get_children(node)))
    return result

from functools import reduce, partial
from operator import iconcat
from typing import Iterable, Callable, Optional

from app.basic import get_fathers_by_rules, get_children_by_rules
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


def get_roots_by_rules(rules: set[Rule], variable: Variable) -> set[Variable]:
    target_variables: set[Variable] = {variable}
    clone_rules = set(rules)
    while True:
        get_fathers: Callable[[Variable], Iterable[Variable]] = partial(get_fathers_by_rules, clone_rules)
        fathers_variables: list[Variable] = list(reduce_ior(map(get_fathers, target_variables)))
        if len(fathers_variables) == 0:
            return target_variables
        target_variables = set(fathers_variables)


def from_table_to_model() -> tuple[set[Rule], list[Variable]]:
    with get_session() as session:
        stub_var = Variable('', set())
        values: dict[int, Value] = {v.id: Value(v.name, v.order, stub_var) for v in session.query(ValueTable)}
        variables: dict[int, Variable] = {v.id: to_variable(v, values) for v in session.query(VariableTable)}
        rules: set[Rule] = {
            Rule(
                {values[p.id] for p in r.premises},
                {values[c.id] for c in r.conclusions}
            )
            for r in session.query(RuleTable)
        }
        get_roots: Callable[[Variable], set[Variable]] = partial(get_roots_by_rules, rules)
        roots: set[Variable] = reduce_ior(map(get_roots, variables.values()))
        walk: Callable[[Variable], list[Variable]] = partial(walk_by_lvl, partial(get_children_by_rules, rules))
        variables_with_lvl: list[list[Variable]] = list(map(walk, roots))
        ordered_by_len: list[list[Variable]] = sorted(variables_with_lvl, key=len, reverse=True)
        flatted: list[Variable] = reduce(iconcat, ordered_by_len, list())
        return rules, flatted


def walk_by_lvl(get_children: Callable[[Variable], Iterable[Variable]], root: Variable) -> list[Variable]:
    result: list[Variable] = []
    input_: list[Optional[Variable]] = [root]
    while len(input_) > 0:
        node = input_.pop(0)
        if node is None:
            continue
        result.append(node)
        input_.extend(get_children(node))
    return result[::-1]

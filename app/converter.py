from functools import reduce, partial
from operator import iconcat
from typing import Iterable, Callable, Optional

from app.basic import get_children_by_rules, get_parents_by_rules, get_conclusions_variables, \
    filter_variable_in_premises
from app.custom_functions import reduce_or
from app.models import Variable, Option, Rule
from database import get_session
from database.tables import VariableTable, OptionTable, RuleTable, SelectedOptionTable


def to_option(selected_option: SelectedOptionTable, option_table: OptionTable, variable: Variable) -> Option:
    return Option(
        option_table.id,
        option_table.value,
        selected_option.scalar,
        option_table.order,
        variable
    )


def to_variable(variable_table: VariableTable, values: dict[int, Option]) -> Variable:
    variable = Variable(variable_table.id, variable_table.question, set(), variable_table.is_scalar)
    for value_table in variable_table.options:
        value = values[value_table.id]
        value.variable = variable
        variable.options.add(value)

    return variable


def get_roots_by_rules(rules: set[Rule], variable: Variable) -> set[Variable]:
    target_variables: set[Variable] = {variable}
    clone_rules = set(rules)
    while True:
        get_fathers: Callable[[Variable], Iterable[Variable]] = partial(get_children_by_rules, clone_rules)
        fathers_variables: list[Variable] = list(reduce_or(map(get_fathers, target_variables)))
        if len(fathers_variables) == 0:
            return target_variables
        target_variables = set(fathers_variables)


def from_table_to_model() -> tuple[set[Rule], list[Variable]]:
    with get_session() as db:
        stub_var = Variable('', '', set(), False)
        values: dict[int, Option] = {v.id: Option(v.id, v.value, '0', v.order, stub_var) for v in db.query(OptionTable)}
        variables: dict[int, Variable] = {v.id: to_variable(v, values) for v in db.query(VariableTable)}
        rules: set[Rule] = {
            Rule(
                {values[p.id] for p in r.premises},
                {values[c.id] for c in r.conclusions},
                r.formula
            )
            for r in db.query(RuleTable)
        }
        get_roots: Callable[[Variable], set[Variable]] = partial(get_roots_by_rules, rules)
        roots: set[Variable] = reduce_or(map(get_roots, variables.values()))
        walk: Callable[[Variable], list[Variable]] = partial(walk_by_lvl, partial(get_parents_by_rules, rules))
        variables_with_lvl: list[list[Variable]] = list(map(walk, roots))
        ordered_by_len: list[list[Variable]] = sorted(variables_with_lvl, key=len, reverse=True)
        flatted: list[Variable] = reduce(iconcat, ordered_by_len, list())
        return rules, flatted


def walk_by_lvl(get_parents: Callable[[Variable], Iterable[Variable]], root: Variable) -> list[Variable]:
    result: list[Variable] = []
    input_: list[Optional[Variable]] = [root]
    while len(input_) > 0:
        node = input_.pop(0)
        if node is None:
            continue
        result.append(node)
        input_.extend(get_parents(node))
    return result[::-1]


def cut_branch(branch: Variable, rules: set[Rule]) -> tuple[set[Rule], list[Variable]]:
    target_variables: list[Variable] = [branch]
    accumulated_vars: list[Variable] = list()
    accumulated_rules: set[Rule] = set()
    while True:
        if len(target_variables) == 0:
            return accumulated_rules, accumulated_vars
        variable: Variable = target_variables.pop()
        accumulated_vars.append(variable)
        added_rules: set[Rule] = set(filter_variable_in_premises(rules, variable))
        accumulated_rules.update(added_rules)
        added_variables: set[Variable] = reduce_or(map(get_conclusions_variables, added_rules))
        accumulated_vars.extend(added_variables)
        target_variables.extend(added_variables)
